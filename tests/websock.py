# import websockets 

# import asyncio

# async def handle(websockets, path):
#     data =  await websockets.recv()
#     reply =  f"Data received as: {data}"
#     await websockets.send(reply)
    
    
# star_server = websockets.serve(handle, "localhost" , 8000)

# asyncio.get_event_loop().run_until_complete(star_server)
# asyncio.get_event_loop().run_forever()

# import os  
# from datetime import  datetime, timezone
# from models.menuModel import  timeFormatOk


# print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

# formatStr = '%H:%M'


#     # raise RuntimeError(f'this is a short error {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}', 'line 4')
#     # print(timeFormatOk('12:59'))
#     # print(timeFormatOk('2:7'))
#     # print(timeFormatOk('24:44'))
    

# end  =  datetime.strptime('14:59', formatStr).replace(tzinfo=timezone.utc).timestamp()
# start = datetime.strptime('13:7', formatStr).replace(tzinfo=timezone.utc).timestamp()

# now  = datetime.now().strftime(formatStr)

# nowTimeStamp = datetime.strptime(datetime.now().strftime(formatStr), formatStr).replace(tzinfo=timezone.utc).timestamp()

# if end >= nowTimeStamp and   nowTimeStamp >=start: 
#     print(True)

# else:
#     print(False)



# print(now)
import  string
import  random 

def secure(accessable: bool): 
    
    def inner(func): 
        def wrapper(*args, **kwargs): 
            if accessable : 
                return  func(*args, **kwargs)
            
            print("Not accessable function")
            return None 

        return wrapper     
    return inner 

@secure(accessable=False)
def generateSecretKey(nr:int):
    
    return ''.join(random.choice(string.printable) for _ in range(nr))



if __name__ == '__main__': 
    
    print(generateSecretKey(32))
