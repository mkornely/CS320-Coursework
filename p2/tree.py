# project:p2

# submitter:mkornely

# partner:none 

# hours:7


from zipfile import ZipFile
import csv 
from io import TextIOWrapper


class ZippedCSVReader:
    def __init__(self,zipfile):
        self.paths=[]
        self.zipfile=zipfile
        with ZipFile(zipfile) as zf:
            for info in zf.namelist():
                self.paths.append(info)
        self.paths=sorted(self.paths)

    def rows(self,filename=None):
        with ZipFile(self.zipfile) as zf:
            if(filename != None):
                with zf.open(filename, 'r') as file:
                    dictreader = csv.DictReader(TextIOWrapper(file, 'utf-8'))
                    for x in dictreader:
                        yield x        
            else:
                for x in self.paths:
                    with zf.open(x, 'r') as file:
                        dictreader = csv.DictReader(TextIOWrapper(file, 'utf-8'))
                        for x in dictreader:
                            yield x                   
                            
class Loan:
    def __init__(self, amount, purpose, race, sex, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.sex = sex
        self.income = income
        self.decision = decision

    def __repr__(self):
        return 'Loan(' + str(self.amount) + ", '" +self.purpose + "', '" + self.race + "', '" +self.sex + "', "+ str(self.income) + ", '" +self.decision + "')"

    def __getitem__(self, lookup):
        try:
            item=getattr(self,lookup)
            return item
        except AttributeError:
            for x in dir(self):
                if(getattr(self,x)==lookup):
                    return 1
            return 0
        
        
        
class Bank: 
    def __init__(self, name, reader):
        self.name= name
        self.reader=reader
    
    def loans(self):
        for x in self.reader.rows(): 
            for key, value in x.items():
                if value == '':
                    x[key] = '0'
            
            bankname= x["agency_abbr"]
            if(self.name is not None):
                if(bankname!= self.name):
                    continue
                
            loanamount= int(x["loan_amount_000s"])
            purpose=x["loan_purpose_name"]
            race=x["applicant_race_name_1"]
            sex=x["applicant_sex_name"]
            income= int(x["applicant_income_000s"])
            action=int(x["action_taken"])
            
            if(action==1):
                decision="approve"
            else:
                decision="deny"
            
            newloan= Loan(loanamount, purpose, race, sex, income, decision)           
            yield newloan

    
def get_bank_names(reader):
    banknames=[]
    for x in reader.rows(): 
        bankname= x["agency_abbr"]
        banknames.append(bankname)
    
    banknames=list(set(banknames))
    
    return sorted(banknames)   
 
                
class SimplePredictor():
    def __init__(self):
        self.approved=0
        self.denied=0

    def predict(self, loan):
        if(loan.purpose== "Refinancing"):
            self.approved+=1
            return True
        else:
            self.denied+=1
            return False

    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied 

    
class Node(SimplePredictor):
    def __init__(self, field, threshold, left, right):
        super().__init__()       

        self.field= field
        self.threshold=threshold
        self.left=left
        self.right= right 

    def dump(self, indent=0):
        if self.field == "class":
            line = "class=" + str(self.threshold)
        else:
            line = self.field + " <= " + str(self.threshold)
        print("  "*indent+line)
        if self.left!= None:
            self.left.dump(indent+1)
        if self.right != None:
            self.right.dump(indent+1)
        
    def node_count(self):
        if self.left is None and self.right is None:
            return 1 
        if self.left is None:
            return 1+ self.right.node_count()
        if self.right is None:
            return 1+ self.right.node_count()      
        else:
            return 1+ self.right.node_count() + self.left.node_count()
   
    def predict(self,loan):
        if self.field=="class":
            prediction=bool(int(self.threshold))
            return prediction
                     
        if float(loan[self.field]) <= float(self.threshold):  
            prediction= self.left.predict(loan)
        
        if float(loan[self.field]) >= float(self.threshold):
            prediction= self.right.predict(loan)
    
        if prediction:
            self.approved+=1
        else:
            self.denied+=1
            
        return prediction
        
def build_tree(rows, root_idx=0):
    x=rows[root_idx]
   
    if x['field']=="class":
        return Node(field=x['field'], threshold=x['threshold'], left=None, right=None)
   
    else:
        return Node(field=x['field'], threshold=x['threshold'], left=build_tree(rows,int(x['left'])), right=build_tree(rows,int(x['right'])))

    
    
def bias_test(bank, predictor, field, value_override):
    bias=0
    totalloans=0
    
    for x in bank.loans():
        totalloans+=1
        prechange_prediction= predictor.predict(x)
        if field=='sex':
            changedloan= Loan(x['amount'],x['purpose'], x['race'],value_override,x['income'],x['decision'])
            
        if field=='race':
            changedloan=Loan(x['amount'],x['purpose'],value_override,x['sex'],x['income'],x['decision'])
            
        changed_prediction=predictor.predict(changedloan)
        
        if(changed_prediction!=prechange_prediction):
            bias=bias+1
            
    return (bias/totalloans)
    
    
    

      
    