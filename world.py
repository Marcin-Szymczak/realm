import array

material = {
    "void":{
        "solid":False,
        #"flammability":0,
    },
    "air":{
        "solid":False,
        #"flammability":0,
    },
    "stone":{
        "solid":True,
        #"flammability":0,
    },
    "wood":{
        #"flammability":60,
    }
}

material_index = ["void","air","stone","wood"]

for index, mat in enumerate(material_index):
    material[mat]["id"] = index

print(material)

class Level:
    def __init__(self,width,height,depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.data = [0 for i in range(2*width*height)]
        
    def generate(self, world_type):
        if world_type == "giant room":
            for i in range(0,self.width):
                self.set_tile(i,0,0,1)
                self.set_tile(i,self.height-1,0,1)

            for i in range(0,self.height):
                self.set_tile(0,i,0,1)
                self.set_tile(self.width-1,i,0,1)
    
    def get_tile(self,x,y,z):
        if x < 0 or x >= self.width or \
           y < 0 or y >= self.height or \
           z < 0 or z >= self.depth:
           return 0

        return self.data[x+self.width*y + self.width*self.height*z]

    def set_tile(self,x,y,z,new_value):
        if x < 0 or x >= self.width or \
           y < 0 or y >= self.height or \
           z < 0 or z >= self.depth:
            return
        if isinstance(new_value, str):
            new_value = material_index[new_value]

        self.data[x + self.width*y + self.width*self.height*z] = new_value
