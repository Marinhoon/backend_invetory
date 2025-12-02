from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime

produtos_bp = Blueprint('produtos', __name__)


@produtos_bp.route('', methods=['GET'])
def get_produtos():
    try:
        produtos_collection = current_app.db['produtos']
        produtos = list(produtos_collection.find({}))

        # Converter ObjectId para string
        for produto in produtos:
            produto['_id'] = str(produto['_id'])

        return jsonify(produtos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@produtos_bp.route('/<codigo>', methods=['GET'])
def get_produto(codigo):
    try:
        produtos_collection = current_app.db['produtos']
        produto = produtos_collection.find_one({'codigo': codigo})

        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404

        produto['_id'] = str(produto['_id'])
        return jsonify(produto), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@produtos_bp.route('', methods=['POST'])
def create_produto():
    try:
        data = request.get_json()
        produtos_collection = current_app.db['produtos']

        novo_produto = {
            'codigo': data.get('codigo'),
            'nome': data.get('nome'),
            'quantidade': data.get('quantidade', 0),
            'valorUnitario': data.get('valorUnitario', 0),
            'valorCompra': data.get('valorCompra', 0),
            'unidade': data.get('unidade', 'UN'),
            'ncm': data.get('ncm'),
            'ean': data.get('ean'),
            'ultimaAtualizacao': datetime.utcnow()
        }

        result = produtos_collection.insert_one(novo_produto)
        novo_produto['_id'] = str(result.inserted_id)

        return jsonify(novo_produto), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@produtos_bp.route('/<codigo>', methods=['PUT'])
def update_produto(codigo):
    try:
        data = request.get_json()
        produtos_collection = current_app.db['produtos']

        update_data = {
            'nome': data.get('nome'),
            'quantidade': data.get('quantidade'),
            'valorUnitario': data.get('valorUnitario'),
            'valorCompra': data.get('valorCompra'),
            'unidade': data.get('unidade'),
            'ncm': data.get('ncm'),
            'ean': data.get('ean'),
            'ultimaAtualizacao': datetime.utcnow()
        }

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        result = produtos_collection.update_one(
            {'codigo': codigo},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Produto não encontrado'}), 404

        produto = produtos_collection.find_one({'codigo': codigo})
        produto['_id'] = str(produto['_id'])

        return jsonify(produto), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@produtos_bp.route('/<codigo>', methods=['DELETE'])
def delete_produto(codigo):
    try:
        produtos_collection = current_app.db['produtos']
        result = produtos_collection.delete_one({'codigo': codigo})

        if result.deleted_count == 0:
            return jsonify({'error': 'Produto não encontrado'}), 404

        return jsonify({'message': 'Produto deletado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@produtos_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        produtos_collection = current_app.db['produtos']

        total_produtos = produtos_collection.count_documents({})
        zerados = produtos_collection.count_documents({'quantidade': 0})
        baixo_estoque = produtos_collection.count_documents({
            'quantidade': {'$gt': 0, '$lt': 10}
        })

        valor_total = sum([p.get('valorCompra', 0) * p.get('quantidade', 0)
                           for p in produtos_collection.find({})])

        return jsonify({
            'total_produtos': total_produtos,
            'zerados': zerados,
            'baixo_estoque': baixo_estoque,
            'valor_total': valor_total
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
