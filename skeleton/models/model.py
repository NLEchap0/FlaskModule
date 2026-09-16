from models.conn import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(260))
    price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        out = {
            'id':self.id,
            'name':self.name,
            'description':self.description,
            'price':self.price,
        }
        # out['id'] = self.id
        # out['name'] = self.name
        # out['description'] = self.description
        # out['price'] = self.price
        return out
        
    