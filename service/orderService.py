from datetime import  datetime, timezone  

formatStr = '%H:%M'


def isActive(startTime: str , endTime: str)-> bool :
    start = datetime.strptime(startTime, formatStr).replace(tzinfo=timezone.utc).timestamp()
    end  =  datetime.strptime(endTime, formatStr).replace(tzinfo=timezone.utc).timestamp()
    now =  datetime.strptime(datetime.now().strftime(formatStr), formatStr).replace(tzinfo=timezone.utc).timestamp()
        
    if now<=end and now>=start: 
        return True
    else: 
        return False