import sys, os, zlib
from pathlib import Path

def search_git(path, target):
    for name in os.listdir(path):
        if name == target:
            return True
    return False



class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()
  

def recursive_search(node1, short_path, root_commits, visited, objects_path):

    f = open(short_path, 'rb')
    message = zlib.decompress(f.read())
    f.close()
    message = message.decode('utf-8')
    message_list = message.split('\n')

    parent_hashes = list()
    for m in message_list:
        if m[0:6] == "parent":
            branch_hash = m[7:len(m)]
            parent_hashes.append(branch_hash)

    flag = True # whether it has parents at all
    if parent_hashes == list(): # if no parent
        flag = False
        if node1.commit_hash not in visited:
            root_commits.append(node1)
            visited.add(node1.commit_hash)

    if flag == True: # if there are parents
        for p_h in parent_hashes:
            if p_h not in visited:
                node2 = CommitNode(p_h)

            if node1.commit_hash not in visited:
                node1.parents.add(p_h)
            else:
                for i in range(len(root_commits)): # search for index in root_commits
                    if root_commits[i].commit_hash == node1.commit_hash:
                        root_commits[i].parents.add(p_h)

            if p_h not in visited:
                node2.children.add(node1.commit_hash)
            else:
                for i in range(len(root_commits)):
                    if root_commits[i].commit_hash == p_h:
                        root_commits[i].children.add(node1.commit_hash)

            if node1.commit_hash not in visited:
                root_commits.append(node1)
                visited.add(node1.commit_hash)
            if p_h not in visited:
                root_commits.append(node2)
                visited.add(p_h)
            
            first_two = p_h[0:2]
            the_rest = p_h[2:len(p_h)]

            short_path = objects_path + '/' + first_two + '/' + the_rest

            if p_h not in visited:
                root_commits = recursive_search(node2, short_path, root_commits, visited, objects_path)
            else:
                for i in range(len(root_commits)):
                    if root_commits[i].commit_hash == p_h:
                        root_commits = recursive_search(root_commits[i], short_path, root_commits, visited, objects_path)

    return root_commits



def topo_order_commits():
    # First find where .git is

    target = ".git"
    current_dir = os.getcwd()

    while(search_git(current_dir, target) == False):
        if current_dir == '/':
            sys.stderr.write("Not inside a Git repository")
            exit(1)
        current_dir = Path(current_dir).parent


    # Second find branch names

    refs_path = current_dir + "/.git/refs"
    objects_path = current_dir + "/.git/objects"

    heads_path = refs_path + "/heads"

    branch_names = os.listdir(heads_path)








    # Third find the commit nodes in all branches
    root_commits = list() # the result

    visited = set()

    for b in branch_names:
        branch_locate = heads_path + '/' + b
        branch = open(branch_locate, 'r')
        branch_hash = branch.read()
        branch.close()

        first_two = branch_hash[0:2]
        the_rest = branch_hash[2:(len(branch_hash)-1)]

        short_path = objects_path + '/' + first_two + '/' + the_rest

        node1 = CommitNode(branch_hash[0:(len(branch_hash)-1)])


        root_commits = recursive_search(node1, short_path, root_commits, visited, objects_path)




    # Fourth topological order
    result_stack = []
    visited = set()

    current = root_commits[0]

    flagg = True # whether all the nodes have been visited
    while flagg == True:
        flag = False # whether it has unvisited children
        if current.children != set():
            for c in current.children:
                if c not in visited:
                    flag = True

                    for n in root_commits:
                        if n.commit_hash == c:
                            current = n
                    break

        if flag == False: # if the current node has no unvisited children
            result_stack.append(current)
            visited.add(current.commit_hash)

            i = -1 # search the index of current
            for c in root_commits:
                i = i + 1
                if c == current:
                    break

            root_commits.pop(i)

            flag2 = False # whether it has unvisited parent
            if current.parents != set():
                for p in current.parents:
                    if p not in visited:
                        flag2 = True

                        for n in root_commits: # search the node containing parent hash
                            if n.commit_hash == p:
                                current = n

                        break

            if flag2 == False: # if the current node has no unvisited parent
                if root_commits != list(): # if the node still has hope
                    current = root_commits[0]
                else:
                    flagg = False


    # Fifth print the commit hashes

    for i in range(len(result_stack)):
        to_print = result_stack[i].commit_hash
        dict_list = list()
        for b in branch_names:
            branch_locate = heads_path + '/' + b
            branch = open(branch_locate, 'r')
            branch_hash = branch.read()
            branch.close()
            branch_hash = branch_hash[0:(len(branch_hash)-1)]
            if branch_hash == result_stack[i].commit_hash:
                dict_list.append(b)
        dict_list.sort()
        for d in dict_list:
            to_print = to_print + " " + d
        print(to_print)


        if i == (len(result_stack) - 1):
            break

        to_print = ""
        if result_stack[i+1].commit_hash not in result_stack[i].parents:
            if len(result_stack[i].parents) == 0:
                to_print = to_print + "=\n\n="
            else:
                tmp_list = list(result_stack[i].parents)
                for j in range(len(tmp_list)):
                    if j == (len(tmp_list) - 1):
                        to_print = to_print + tmp_list[j]
                    else:
                        to_print = to_print + tmp_list[j] + ' '
                to_print = to_print + "=\n\n="

            tmp_list = list(result_stack[i + 1].children)
            if len(tmp_list) > 0:
                for k in range(len(tmp_list)):
                    if k == (len(tmp_list) - 1):
                        to_print = to_print + tmp_list[k]
                    else:
                        to_print = to_print + tmp_list[k] + ' '


            print(to_print)
















if __name__ == '__main__':
    topo_order_commits()
