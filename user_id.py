class UserId:
    user_id: dict
    id_user: dict
    
    def __init__(self):
        self.user_id = dict()
        self.id_user = dict()
        
    def AddUserId(self, user, id):
        self.user_id[user] = id
        self.id_user[id] = user
        
    def GetId(self, user):
        return self.user_id[user]
    
    def GetUser(self, id):
        return self.id_user[id]
    
    def IdExists(self, id) -> bool:
        return id in self.id_user.keys()
    
    def IdsExist(self, ids: list):
        keys = self.id_user.keys()
        for id in ids:
            if not id in keys:
                return False
        return True
    
GlobalUserId = UserId()