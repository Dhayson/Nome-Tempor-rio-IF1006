from discord import User, Role

class UserId:
    user_id: dict
    id_user: dict
    
    def __init__(self):
        self.user_id = dict()
        self.id_user = dict()
        
    def AddUserId(self, user, id):
        print(f"added id {id}")
        self.user_id[user] = id
        self.id_user[id] = user
        
    def GetId(self, user) -> int:
        return self.user_id[user]
    
    def GetUser(self, id) -> User | None:
        return self.id_user.get(id)
    
    def IdExists(self, id) -> bool:
        return id in self.id_user.keys()
    
    def IdsExist(self, ids: list) -> bool:
        keys = self.id_user.keys()
        for id in ids:
            if not id in keys:
                return False
        return True
    
GlobalUserId = UserId()

class RoleId:
    role_id: dict
    id_role: dict
    
    def __init__(self):
        self.role_id = dict()
        self.id_role = dict()
        
    def AddRoleId(self, user, id):
        print(f"added role id {id}")
        self.role_id[user] = id
        self.id_role[id] = user
        
    def GetId(self, user) -> int:
        return self.role_id[user]
    
    def GetRole(self, id) -> Role | None:
        return self.id_role.get(id)
    
    def IdExists(self, id) -> bool:
        return id in self.id_role.keys()
    
    def IdsExist(self, ids: list) -> bool:
        keys = self.id_role.keys()
        for id in ids:
            if not id in keys:
                return False
        return True
    
GlobalRoleId = RoleId()