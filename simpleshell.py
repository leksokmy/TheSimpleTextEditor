

namespace = {}
while True:
    try:
        line = input('>>> ')          
    except EOFError:
        break
    else:
        exec(line, namespace)        
