
import re

def IsList(val):
  return isinstance(val, dict)

def ParseChangePath(path):
  strs = re.split('\.|\[|\]', path)
  
  assign_str = ""
  elems = []
  for str in strs:
    if(len(str) > 0):
      assign_str += "[\"" + str + "\"]"
      elems.append(str)

  return { "assign": assign_str, "elems": elems, "path": path }

def ParseChangeNotification(str):
  first_space = str.find(' ')
  if(first_space == -1):
    return None
  
  operation = str[0 : first_space]
  if(operation == "kClear" or operation == "kCompress"):
    temp_path = ParseChangePath(str[first_space + 1:])
    return { "op": operation, "path": temp_path }
  
  first_space += 1
  next_space = str.find(' ', first_space)
  if(next_space == -1):
    return None
  
  path = ParseChangePath(str[first_space: next_space])
  
  next_space += 1
  
  if(operation == "kSet"):
    data = str[next_space:]
    return { "op": operation, "path": path, "data": data }
  
  if(operation == "kRemove"):
    data = str[next_space:]
    return { "op": operation, "path": path, "index": data }

  if(operation == "kInsert"):
    final_space = str.find(' ', next_space)
    insert_index = str[next_space : final_space]
    insert_data = str[final_space + 1:]
    return { "op": operation, "path": path, "index": insert_index, "data": insert_data }
  
  return None

def GetValueAtPath(path, obj):
  return eval("obj" + path["assign"])

def ApplyChangeNotification(change, obj):
  if(change == None):
    return obj

  false = False
  true = True

  if(change["op"] == "kSet"):
    set_eval_data = "obj" + change["path"]["assign"] + " = " + change["data"].replace("\\/", "/")
    exec(set_eval_data)
  
  if(change["op"] == "kClear"):
    clear_eval_data = "obj" + change["path"]["assign"] + " = {}"
    exec(clear_eval_data)
  
  if(change["op"] == "kInsert"):
    insert_eval_data = "obj" + change["path"]["assign"] + "[\"" + change["index"] + "\"] = " + change["data"].replace("\\/", "/")
    exec(insert_eval_data)
  
  if(change["op"] == "kRemove"):
    remove_eval_data = "del obj" + change["path"]["assign"] + "[\"" + change["index"] + "\"]"
    exec(remove_eval_data)
  
  return obj

def CreateChangeCallback(callback_list, obj, change_path, onset_cb):
  path = ParseChangePath(change_path)
  callback_list.append({
    "path": path,
    "defunct": False,
    "onset": onset_cb
  })
 
  if(PathExistsInObject(path, obj)):
    onset_cb(GetValueAtPath(path, obj))

def CreateListChangeCallback(callback_list, obj, change_path, oninsert_cb, onmodify_cb, onremove_cb, onclear_cb):
  path = ParseChangePath(change_path)
  callback_list.append({
    "path": path,
    "defunct": False,
    "oninsert": oninsert_cb,
    "onmodify": onmodify_cb,
    "onremove": onremove_cb,
    "onclear": onclear_cb
  })
  
  onclear_cb()
  if(PathExistsInObject(path, obj)):
    val = GetValueAtPath(path, obj)
    if(type(val) is list):
      for e in val:
        oninsert_cb(e, val[e])

def RemoveChangeCallback(callback_list, change_path):
  for elem in callback_list:
    if(elem.path["path"] == change_path and elem['defunct'] == False):
      elem['defunct'] = True
      return

def CleanupCallbackList(callback_list):
  index = len(callback_list) - 1
  while index >= 0:
    if(callback_list[index]['defunct']):
      callback_list.remove(callback_list[index])
    index -= 1

def PathExistsInObject(path, obj):
  obj_ptr = obj

  for elem in path["elems"]:
    if(elem in obj_ptr):
      obj_ptr = obj_ptr[elem]
    else:
      return False

  return True

def CallChangeCallbacks(change, callback_list, obj):

  if(change["op"] == "kSet"):
    HandleSetChange(change, callback_list, obj)
  
  if(change["op"] == "kClear"):
    HandleClearChange(change, callback_list, obj)
  
  if(change["op"] == "kInsert"):
    HandleInsertChange(change, callback_list, obj)
  
  if(change["op"] == "kRemove"):
    HandleRemoveChange(change, callback_list, obj)

  CleanupCallbackList(callback_list)

def HandleSetChange(change, callback_list, obj):
  change_path = change["path"]

  for callback in callback_list:
    callback_path = callback["path"]
    
    if(callback["defunct"]):
      continue
            
    if(len(change_path["path"]) < len(callback_path["path"])):
      if(callback_path["path"][:len(change_path["path"])] == change_path["path"]):

        if(PathExistsInObject(callback_path, obj)):
          val = GetValueAtPath(callback_path, obj)
            
          if("onset" in callback):
            callback['onset'](val)
            
          if("onclear" in callback):
            callback['onclear']()
            
          if("oninsert" in callback and IsList(val)):
            for idx, e in val.iteritems():
              callback['oninsert'](idx, e)

        else:
          if("ondelete" in callback):
            callback['ondelete']()

    else:
      if(change_path["path"][:len(callback_path["path"])] == callback_path["path"]):
     
        parent_val = GetValueAtPath(callback_path, obj)
          
        if("onset" in callback):
          callback['onset'](parent_val)
          
        if("onmodify" in callback):
          sub_index = change_path["elems"][len(callback_path["elems"])]
          callback['onmodify'](sub_index, parent_val[sub_index])

def HandleClearChange(change, callback_list, obj):
  change_path = change["path"]

  for callback in callback_list:
    callback_path = callback["path"]
    
    if(callback["defunct"]):
      continue
            
    if(len(change_path["path"]) < len(callback_path["path"])):
      if(callback_path["path"][:len(change_path["path"])] == change_path["path"]):
        if("ondelete" in callback):
          callback['ondelete']()
        
        if("onclear" in callback):
          callback['onclear']()

    elif(change_path["path"] == callback_path["path"]):
      if("onclear" in callback):
        callback['onclear']()
    elif(change_path["path"][:len(callback_path["path"])] == callback_path["path"]):            
      if("onmodify" in callback):
        parent_val = GetValueAtPath(callback_path, obj)
        sub_index = change_path["elems"][len(callback_path["elems"])]
        callback['onmodify'](sub_index, parent_val[sub_index])


def HandleInsertChange(change, callback_list, obj):
  change_path = change["path"]
  elem_path = change_path["path"] + '[' + change["index"] + ']'

  for callback in callback_list:
    callback_path = callback["path"]
    
    if(callback["defunct"]):
      continue
    
    if(len(elem_path) < len(callback_path["path"])):
      if(callback_path["path"][:len(elem_path)] == elem_path):

        if(PathExistsInObject(callback_path, obj)):
          val = GetValueAtPath(callback_path, obj)
            
          if("onset" in callback):
            callback['onset'](val)

          if("onclear" in callback):
            callback['onclear']()

          if("oninsert" in callback and IsList(val)):
            for idx, e in val.iteritems():
              callback['oninsert'](idx, e)

    elif(change_path["path"] == callback_path["path"]):
      if("oninsert" in callback):
        matching_val = GetValueAtPath(callback_path, obj)
        callback['oninsert'](change["index"], matching_val[change["index"]])

    elif(change_path["path"][:len(callback_path["path"])] == callback_path["path"]):   
      if("onmodify" in callback):
        parent_val = GetValueAtPath(callback_path, obj)
        sub_index = change_path["elems"][len(callback_path["elems"])]
        callback['onmodify'](sub_index, parent_val[sub_index])

def HandleRemoveChange(change, callback_list, obj):
  change_path = change["path"]
  elem_path = change_path["path"] + '[' + change["index"] + ']'

  for callback in callback_list:
    callback_path = callback["path"]
    
    if(callback["defunct"]):
      continue
    
    if(len(elem_path) < len(callback_path["path"])):
      if(callback_path["path"][:len(elem_path)] == elem_path):

        if("ondelete" in callback):
          callback['ondelete']()
          
        if("onclear" in callback):
          callback['onclear']()

    elif(change_path["path"] == callback_path["path"]):
      if("onremove" in callback):
        callback['onremove'](change["index"])

    elif(change_path["path"][:len(callback_path["path"])] == callback_path["path"]):   
      if("onmodify" in callback):
        parent_val = GetValueAtPath(callback_path, obj)
        sub_index = change_path["elems"][len(callback_path["elems"])]
        callback['onmodify'](sub_index, parent_val[sub_index])


def ClearChangeCallbacks(callback_list):

  for callback in callback_list:
    
    if("ondelete" in callback):
      callback['ondelete']()
    
    if("onclear" in callback):
      callback['onclear']()



