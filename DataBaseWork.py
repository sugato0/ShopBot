import sqlite3
class DataBase:
    def __init__(self):

        self.conn = sqlite3.connect('userLoginToQIWI.db')
        self.cur = self.conn.cursor()
    def addNewPAID(self,id_user, user_name, bill_id, products,countProducts):
        userPAIDData = (int(id_user),str(user_name),str(bill_id),str(products),str(countProducts))
        self.cur.execute("INSERT INTO 'check' (id_user, user_name, bill_id, products,countProducts) VALUES(?, ?, ?,?,?);",userPAIDData)
        self.conn.commit()
    def isWasPaid(self,bill_id):
        userPAIDData = (str(bill_id),)
        self.s = self.cur.execute("SELECT bill_id FROM 'check' WHERE bill_id IN (?);",userPAIDData).fetchall()
        self.conn.commit()
        return bool(self.s)