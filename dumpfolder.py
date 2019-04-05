import os,sys,configparser,json
from os.path import join
import tornado.ioloop
import tornado.web

root_name = "thing"
root_section = "root"
inherit_key = "inherit_from"

def is_schema_configuration(filename):
    return filename != None and filename.endswith(".ini")

def get_configuration_main_name(filename):
    return filename.replace(".ini","") if filename != None else None

def get_main_name_from_class_name(classname):
    return classname.replace("kbo:","") if classname != None else None

def refresh_repo(folder):
    nodes_repo = {}
    relation_repo = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = join(root, file)
            basename = os.path.basename(full_path)
            if is_schema_configuration(basename):
                #record into node repo
                main_name = get_configuration_main_name(basename)
                file_string = ""
                with open(full_path, "r", encoding="utf-8") as f:
                    file_string = f.read()
                nodes_repo[main_name] = (full_path, file_string)
                #record into relation repo
                config = configparser.ConfigParser()
                config.read(full_path)
                if config.has_option(root_section, inherit_key):
                    parent_class = config.get(root_section, inherit_key)
                    parent_name = get_main_name_from_class_name(parent_class)
                    if not parent_name in relation_repo:
                        relation_repo[parent_name] = [main_name]
                    else:
                        relation_repo[parent_name].append(main_name)
    return nodes_repo, relation_repo


def traverse_data(current_visit, relation_repo, nodes_repo, context_list):
    current_node = {}
    current_node["class_name"] = current_visit
    current_node["content"] = nodes_repo[current_visit][1]
    current_node["successors"] = []
    context_list.append(current_node)
    if current_visit in relation_repo:
        children_names = relation_repo[current_visit]
        for child_name in children_names:
            traverse_data(child_name, relation_repo, nodes_repo, current_node["successors"])
        
    
    

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        folder = sys.argv[1]
        nodes_repo,relation_repo = refresh_repo(folder)
        all_thing = []
        traverse_data("thing", relation_repo, nodes_repo, all_thing)
        output_json = json.dumps(all_thing[0], indent=4, sort_keys=True)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(output_json.encode("utf-8"))

application = tornado.web.Application([
    (r'/index', MainHandler)
])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python %s folder_path"%sys.argv[0])
        sys.exit(-1)
    folder = sys.argv[1]
    if not os.path.exists(folder):
        print("%s does not exist"%folder)
        sys.exit(-1)
    application.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()

