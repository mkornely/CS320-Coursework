# project:p3

# submitter:mkornely

# partner:none 

# hours:7


import os, zipfile
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd 
from selenium.common.exceptions import NoSuchElementException



class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        for child in self.go(node):
            self.dfs_search(child)

    def bfs_search(self, node):
        todo=self.go(node)
        self.visited.add(node)
       
        while len(todo)>0:
            current=todo.pop(0)
            self.visited.add(current)
            
            for child in self.go(current):
                if child not in self.visited:
                    todo.append(child)
                    self.visited.add(child)
            
 
        
            
        

class FileScraper(GraphScraper):
    def go(self, node):
        filename= os.getcwd()+ "/file_nodes/"+ node + ".txt"
        f=open(filename)

        lines=list(f)
        lines_nonewline=[]

        for i in lines:
            lines_nonewline.append(i.split('\n')[0])


        returnlist=list(lines_nonewline[1])
        self.BFSorder.append(lines_nonewline[2].split("BFS: ")[1])
        self.DFSorder.append(lines_nonewline[3].split("DFS: ")[1])
        try:
            while True:
                returnlist.remove(" ")

        except ValueError:
            pass

        return returnlist
    
    
    
class WebScraper(GraphScraper):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver

    # these three can be done as groupwork
    def go(self, url):
        self.driver.get(url)
        
        btnbfs = self.driver.find_element_by_id("BFS")
        btnbfs.click()
        
        btndfs=self.driver.find_element_by_id("DFS")
        btndfs.click()


        
        self.BFSorder.append(btnbfs.text)
       
        self.DFSorder.append(btndfs.text)

        page_links =self.driver.find_element_by_id("Pages")
    
        links=page_links.find_elements_by_tag_name("a")
        linkreturn= list()
        for link in links:
            linkreturn.append(link.get_attribute("href"))
        
        return linkreturn


            
        
       
    def dfs_pass(self, start_url):
        self.DFSorder=[]
        self.visited=set()
        self.dfs_search(start_url)
        passworddfs=str()
        for i in self.DFSorder:
            passworddfs+= i
        return passworddfs
            
    def bfs_pass(self, start_url):
        self.BFSorder=[]
        self.visited=set()
        self.bfs_search(start_url)
        passwordbfs=str()
        for i in self.BFSorder:
            passwordbfs+= i
        return passwordbfs
    
    # write the code for this one individually
    def protected_df(self, url, password):
        self.driver.get(url)

        password_list=list(password)
        
        for i in password: 
            btn = self.driver.find_element_by_id("btn" + i)
            btn.click()
        
        go_btn=self.driver.find_element_by_id("attempt-button")
        go_btn.click()
        time.sleep(1)
        
        length=0; 
        
        
        while(True):
            datatable= pd.read_html(self.driver.page_source)
           
            if length== len(datatable[0]):
                break;
                
            length=len(datatable[0])
            location_btn = self.driver.find_element_by_id("more-locations-button")
            location_btn.click()
            
            time.sleep(1)


        
        return datatable[0]


                


    
    
    
        
        

    