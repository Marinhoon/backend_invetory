from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET

nfes_bp = Blueprint('nfes', __name__)


def parse_nfe_xml(xml_content):
    """Parse XML da NF-e e extrai informações"""
    try:
        root = ET.fromstring(xml_content)

        # Namespace da NF-e
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        # Extrai chave de acesso
        inf_nfe = root.find('.//nfe:infNFe', ns)
        if inf_nfe is None:
            inf_nfe = root.find('.//infNFe')

        chave = inf_nfe.get('Id', '').replace('NFe', '') if inf_nfe is not None else ''

        # Extrai dados da nota
        ide = root.find('.//nfe:ide', ns)
        if ide is None:
            ide = root.find('.//ide')

        numero = ide.find('nNF').text if ide is not None and ide.find('nNF') is not None else ''
        serie = ide.find('serie').text if ide is not None and ide.find('serie') is not None else ''
        data_emissao = ide.find('dhEmi').text if ide is not None and ide.find('dhEmi') is not None else ''

        if not data_emissao and ide is not None:
            data_emissao = ide.find('dEmi').text if ide.find('dEmi') is not None else ''

        # Extrai dados do fornecedor
        emit = root.find('.//nfe:emit', ns)
        if emit is None:
            emit = root.find('.//emit')

        cnpj = emit.find('CNPJ').text if emit is not None and emit.find('CNPJ') is not None else ''
        nome_fornecedor = emit.find('xNome').text if emit is not None and emit.find('xNome') is not None else ''

        # Extrai produtos
        produtos = []
        det_list = root.findall('.//nfe:det', ns)
        if not det_list:
            det_list = root.findall('.//det')

        for idx, det in enumerate(det_list):
            prod = det.find('.//nfe:prod', ns)
            if prod is None:
                prod = det.find('.//prod')

            if prod is not None:
                codigo = prod.find('cProd').text if prod.find('cProd') is not None else ''
                nome = prod.find('xProd').text if prod.find('xProd') is not None else ''
                ncm = prod.find('NCM').text if prod.find('NCM') is not None else ''
                cfop = prod.find('CFOP').text if prod.find('CFOP') is not None else ''
                unidade = prod.find('uCom').text if prod.find('uCom') is not None else 'UN'
                quantidade = float(prod.find('qCom').text) if prod.find('qCom') is not None else 0
                valor_unitario = float(prod.find('vUnCom').text) if prod.find('vUnCom') is not None else 0
                valor_total = float(prod.find('vProd').text) if prod.find('vProd') is not None else 0
                ean = prod.find('cEAN').text if prod.find('cEAN') is not None else None

                produtos.append({
                    'codigo': codigo,
                    'nome': nome,
                    'ncm': ncm,
                    'cfop': cfop,
                    'unidade': unidade,
                    'quantidade': quantidade,
                    'valorUnitario': valor_unitario,
                    'valorTotal': valor_total,
                    'ean': ean if ean and ean != 'SEM GTIN' else None
                })

        # Valor total da nota
        total = root.find('.//nfe:total', ns)
        if total is None:
            total = root.find('.//total')

        valor_total_nfe = float(total.find('vNF').text) if total is not None and total.find('vNF') is not None else 0

        return {
            'chave': chave,
            'numero': numero,
            'serie': serie,
            'dataEmissao': data_emissao,
            'fornecedor': {
                'cnpj': cnpj,
                'nome': nome_fornecedor
            },
            'produtos': produtos,
            'valorTotal': valor_total_nfe,
            'dataProcessamento': datetime.utcnow()
        }
    except Exception as e:
        print(f"[v0] Erro ao fazer parse do XML: {e}")
        return None


@nfes_bp.route('', methods=['GET'])
def get_nfes():
    try:
        nfes_collection = current_app.db['nfes']
        nfes = list(nfes_collection.find({}))

        for nfe in nfes:
            nfe['_id'] = str(nfe['_id'])

        return jsonify(nfes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfes_bp.route('/search', methods=['GET'])
def search_nfes():
    try:
        query = request.args.get('q', '')
        nfes_collection = current_app.db['nfes']

        search_filter = {
            '$or': [
                {'numero': {'$regex': query, '$options': 'i'}},
                {'serie': {'$regex': query, '$options': 'i'}},
                {'chave': {'$regex': query, '$options': 'i'}},
                {'fornecedor.nome': {'$regex': query, '$options': 'i'}},
                {'fornecedor.cnpj': {'$regex': query, '$options': 'i'}}
            ]
        }

        nfes = list(nfes_collection.find(search_filter))

        for nfe in nfes:
            nfe['_id'] = str(nfe['_id'])

        return jsonify(nfes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfes_bp.route('', methods=['POST'])
def create_nfe():
    try:
        files = request.files
        xml_file = files.get('xml')

        if not xml_file:
            return jsonify({'error': 'Arquivo XML é obrigatório'}), 400

        xml_content = xml_file.read()
        nfe_data = parse_nfe_xml(xml_content)

        if not nfe_data:
            return jsonify({'error': 'Erro ao fazer parse do XML'}), 400

        nfes_collection = current_app.db['nfes']
        produtos_collection = current_app.db['produtos']

        # Verifica se NF-e já foi importada
        if nfes_collection.find_one({'chave': nfe_data['chave']}):
            return jsonify({'error': 'Esta NF-e já foi importada'}), 409

        # Atualiza estoque
        for prod in nfe_data['produtos']:
            existing = produtos_collection.find_one({'codigo': prod['codigo']})

            if existing:
                produtos_collection.update_one(
                    {'codigo': prod['codigo']},
                    {'$inc': {'quantidade': prod['quantidade']},
                     '$set': {'valorCompra': prod['valorUnitario'],
                              'valorUnitario': prod['valorUnitario'],
                              'ultimaAtualizacao': datetime.utcnow()}}
                )
            else:
                produtos_collection.insert_one({
                    'codigo': prod['codigo'],
                    'nome': prod['nome'],
                    'quantidade': prod['quantidade'],
                    'valorUnitario': prod['valorUnitario'],
                    'valorCompra': prod['valorUnitario'],
                    'unidade': prod['unidade'],
                    'ncm': prod['ncm'],
                    'ean': prod['ean'],
                    'ultimaAtualizacao': datetime.utcnow()
                })

        # Salva NF-e
        result = nfes_collection.insert_one(nfe_data)
        nfe_data['_id'] = str(result.inserted_id)

        return jsonify(nfe_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfes_bp.route('/<nfe_id>', methods=['GET'])
def get_nfe(nfe_id):
    try:
        nfes_collection = current_app.db['nfes']
        nfe = nfes_collection.find_one({'_id': ObjectId(nfe_id)})

        if not nfe:
            return jsonify({'error': 'NF-e não encontrada'}), 404

        nfe['_id'] = str(nfe['_id'])
        return jsonify(nfe), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
