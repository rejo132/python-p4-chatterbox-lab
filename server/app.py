#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.order_by(Message.created_at.asc()).all()]
        return make_response(jsonify(messages), 200)

    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or not all(key in data for key in ['body', 'username']):
                return make_response(jsonify({'error': 'Missing required fields'}), 400)

            message = Message(
                body=data['body'],
                username=data['username']
            )
            db.session.add(message)
            db.session.commit()

            return make_response(jsonify(message.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    if request.method == 'PATCH':
        try:
            data = request.get_json()
            if not data or 'body' not in data:
                return make_response(jsonify({'error': 'Body field is required'}), 400)

            message.body = data['body']
            db.session.commit()
            return make_response(jsonify(message.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

    elif request.method == 'DELETE':
        try:
            db.session.delete(message)
            db.session.commit()
            return make_response(jsonify({'message': f'Message {id} successfully deleted'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(port=5555)