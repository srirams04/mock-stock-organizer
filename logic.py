import constant
import csv

class InvalidTransactionError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class InvalidCompanyError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class InvalidFileError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message) 


class World:
    def __init__(self, stock_file_name, investors_file_name, load_files = True) -> None:

        if stock_file_name[-4:] != ".csv" or investors_file_name[-4:] != ".csv":
            raise InvalidFileError("Only csv files accepted")
        
        self.companies = {}
        self.latest_indirect_changes = () #Does not include any direct edits made by the user on the application by double clicking
        self.stock_file_name = stock_file_name
        self.investors_file_name = investors_file_name
        self.stock_file_fields = ('name', 'owners', 'location', 'capital', 'stock price', 'shares', 'pr crisis', 'pr response', 'stock drop (pr)', 'latest stock change')
        
        if load_files == False:
            return
            
        try:
            _ = open(stock_file_name, "r")
        except NameError:
            raise InvalidFileError(f"{stock_file_name}: File not found")

        try:
            _ = open(investors_file_name, "r")
        except NameError:
            raise InvalidFileError(f"{investors_file_name}: File not found")
        
        self.init_existing_companies()
        

    def init_existing_companies(self):
        stock_data = self.load_stock_data()
        investors_data = self.load_investors_data()
        
        #Initialising all the companies
        for record in stock_data:
            name = record[0]
            owners = record[1]
            location = record[2]
            capital = round(float(record[3]), 2)
            stock = round(float(record[4]), 2)
            shares = int(record[5])
            pr_crisis = int(record[6])
            pr_response = int(record[7])
            pr_stock_drop = round(float(record[8]), 2)
            latest_stock_change = round(float(record[9]), 2)
            
            self.companies[name] = Company(name, owners, location, capital, stock, shares)
            self.companies[name].set_latest_stock_change(latest_stock_change)
            self.companies[name].set_pr_crisis(pr_crisis)
            self.companies[name].set_pr_response(pr_response)
            self.companies[name].set_stock_drop_pr_crisis(pr_stock_drop)
            

        #Initialising the investors for all the companies
        for investor in investors_data[1:]:
            _dict = {}
            for i in range(len(investor[1:])):
                if int(investor[1:][i]) == 0:
                    continue
                _dict[investors_data[0][1:][i]] = int(investor[1:][i])

            self.companies[investor[0]].set_investors(_dict)
    

    def open_company(self, name, owners, location, capital = 0, stock = 0, shares = 1):
        existing_companies = tuple(i.lower() for i in self.companies.keys())
        
        if name.lower() in existing_companies:
            raise InvalidCompanyError("Company name taken. Think of a new one!")

        x = Company(name, owners, location, capital, stock, shares)
        self.companies[name] = x
        self.dump_stock_data()
        self.dump_investors_data()


    def close_company(self, company_name):
        try:
            company = self.companies[company_name]
        except KeyError:
            raise InvalidCompanyError("Open one before you plan to close it!")


        del self.companies[company.get_name()]
        del company
        self.dump_stock_data()
        self.dump_investors_data()


    def get_owners(self, company_name):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        return self.companies[company_name].get_owners()
    

    def get_location(self, company_name):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        return self.companies[company_name].get_location()
    

    def get_capital(self, company_name):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        return self.companies[company_name].get_capital()
    
    
    def get_stock(self, company_name):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        return self.companies[company_name].get_stock()


    def get_shares(self, company_name):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        if company_name not in self.companies:
            raise InvalidCompanyError
        return self.companies[company_name].get_shares()


    def get_pr_crisis(self, company_name):
        company = self.companies[company_name]
        return company.get_pr_crisis()

    
    def get_pr_response(self, company_name):
        company = self.companies[company_name]
        return company.get_pr_response()


    def get_stock_drop_pr_crisis(self, company_name):
        company = self.companies[company_name]
        return company.get_stock_drop_pr_crisis()


    def get_latest_stock_change(self, company_name):
        company = self.companies[company_name]
        return company.get_latest_stock_change()


    def get_all_stocks(self):
        x = {}
        for i in self.companies:
            x[i] = self.companies[i].get_stock()
        return x
    

    def get_investor_shares(self, company_name, investor_name):
        company = self.companies[company_name]
        return company.get_investor_shares(investor_name)


    def rename(self, old_company_name, new_company_name):
        if old_company_name not in self.companies:
            raise InvalidCompanyError("Open a company before renaming it!")

        self.companies[old_company_name].set_name(new_company_name)
        self.companies[new_company_name] = self.companies.pop(old_company_name)
        
        for company in self.companies.values():
            try:
                shares = company.investors[old_company_name]
                company.add_investor(new_company_name, shares)
                company.remove_investor(old_company_name)
            except KeyError:
                pass
                
        self.dump_stock_data()
        self.dump_investors_data()


    def set_owners(self, company_name, owners):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].set_owners(owners)
        self.dump_stock_data()
    

    def set_location(self, company_name, location):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].set_location(location)
        self.dump_stock_data()


    def set_capital(self, company_name, capital):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].set_capital(capital)
        self.dump_stock_data()
    

    def set_stock(self, company_name, stock):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].set_stock(stock)
        self.dump_stock_data()

    
    def allocate_shares(self, company_name, investor_name, no_of_shares, price):
        if company_name not in self.companies:
            raise InvalidCompanyError("You can't buy shares from a company which doesn't exist!")
        elif investor_name not in self.companies:
            raise InvalidCompanyError("Investing company doesn't exist")
        

        company = self.companies[company_name]
        investor = self.companies[investor_name]

        capital_reqd = price * no_of_shares
        if capital_reqd > investor.get_capital():
            raise InvalidTransactionError("Insufficient Capital")
        
        company.create_shares(investor.get_name(), no_of_shares, price)
        investor.decrease_capital(capital_reqd)

        self.latest_indirect_changes = ((company_name, 'stock price'), (company_name, 'capital'), (company_name, 'shares'), (company_name, 'latest stock change'), (investor_name, 'capital'), (f'{company_name} --> {investor_name}', 'shares fraction'))
        
        self.dump_stock_data()
        self.dump_investors_data()


    def transact_shares(self, company_name, old_investor_name, new_investor_name, no_of_shares, price):
        if company_name not in self.companies:
            raise InvalidCompanyError("You can't transfer the shares of a company which doesn't exist!")
        elif old_investor_name not in self.companies:
            raise InvalidCompanyError("Selling company doesn't exist")
        elif new_investor_name not in self.companies:
            raise InvalidCompanyError("Buying company doesn't exist")

        company = self.companies[company_name]
        old_investor = self.companies[old_investor_name]
        new_investor = self.companies[new_investor_name]

        capital_reqd = price * no_of_shares
        if capital_reqd > new_investor.get_capital():
            raise InvalidTransactionError("Insufficient Capital")

        company.transact_shares(old_investor_name, new_investor_name, no_of_shares, price)
        profit = price * no_of_shares
        new_investor.decrease_capital(profit)
        old_investor.increase_capital(profit)

        self.latest_indirect_changes = ((company_name, 'stock price'), (company_name, 'latest stock change'), (old_investor_name, 'capital'), (new_investor_name, 'capital'), (f'{company_name} --> {old_investor_name}', 'shares fraction'), (f'{company_name} --> {new_investor_name}', 'shares fraction'))

        self.dump_stock_data()
        self.dump_investors_data()


    def release_pr_crisis(self, company_name, num):
        company = self.companies[company_name]
        company.release_pr_crisis(num)

        self.latest_indirect_changes = ((company_name, 'pr crisis'), (company_name, 'pr response'), (company_name, 'stock drop (pr)'), (company_name, 'stock price'), (company_name, 'latest stock change'))
        
        self.dump_stock_data()
    
    
    def release_pr_response(self, company_name, num):
        company = self.companies[company_name]
        company.release_pr_response(num)
        
        self.latest_indirect_changes = ((company_name, 'pr response'), (company_name, 'stock price'), (company_name, 'latest stock change'))

        self.dump_stock_data()
    

    def increase_stock(self, company_name, stock_change):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].increase_stock(stock_change)
        self.dump_stock_data()
    

    def decrease_stock(self, company_name, stock_change):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].decrease_stock(stock_change)
        self.dump_stock_data()
    

    def increase_capital(self, company_name, money):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].increase_capital(money)
        self.dump_stock_data()
    

    def decrease_capital(self, company_name, money):
        if company_name not in self.companies:
            raise InvalidCompanyError("No such company exists")

        self.companies[company_name].decrease_capital(money)
        self.dump_stock_data()


    def load_stock_data(self):
        try:
            file = open(self.stock_file_name, "r")
        except FileNotFoundError:
            file = open(self.stock_file_name, "w", newline = '')
            cwriter = csv.writer(file)
            cwriter.writerow(self.stock_file_fields)
            return tuple()


        creader = csv.reader(file)
        x = tuple(creader)[1:]
        file.close()
        return x
  

    def dump_stock_data(self):
        tup = ()
        for company_name in self.companies:
            company = self.companies[company_name]
            name = company_name
            owners = company.get_owners()
            location = company.get_location()
            capital = company.get_capital()
            stock = company.get_stock()
            shares = company.get_shares()
            pr_crisis = company.get_pr_crisis()
            pr_response = company.get_pr_response()
            pr_stock_drop = company.stock_drop_pr_crisis
            latest_stock_change = company.latest_stock_change
            record = (name, owners, location, capital, stock, shares, pr_crisis, pr_response, pr_stock_drop, latest_stock_change) 
            tup += (record,)
        
        file = open(self.stock_file_name, "w", newline = '')
        cwriter = csv.writer(file)
        cwriter.writerow(self.stock_file_fields)
        cwriter.writerows(tup)
        file.close()
    
    
    def load_investors_data(self):
        file = open(self.investors_file_name, 'r')
        creader = csv.reader(file)
        x = tuple(creader)
        file.close()
        return x

    
    def dump_investors_data(self):
        file = open(self.investors_file_name, "w", newline = '')
        intup = ('',) + tuple(self.companies.keys())
        tup = (intup,)
        for company_name in self.companies:
            intup = (company_name, )
            company = self.companies[company_name]
            for company_name in self.companies:
                if company_name in company.get_investors():
                    ind = company.get_investors()[company_name]
                else:
                    ind = 0
                intup += (ind, )
            tup += (intup,)
        cwriter = csv.writer(file)
        cwriter.writerows(tup)
        file.close()

    
    def reset(self):
        for company in self.companies.values():
            del company
        del self.companies
        self.companies = {}
        self.dump_stock_data()
        self.dump_investors_data()
        
        
class Company():
    def __init__(self, name, owners, location, capital, stock, shares):
        self.name = name
        self.owners = owners
        self.location = location
        self.capital = capital
        self.shares = shares
        self.stock = stock
        self.pr_crisis = 0
        self.pr_response = 0
        self.stock_drop_pr_crisis = 0.0
        self.latest_stock_change = 0.0
        self.investors = {self.name: shares}
    
        
    def get_name(self):
        return self.name


    def get_owners(self):
        return self.owners


    def get_location(self):
        return self.location
    

    def get_capital(self):
        return self.capital
    

    def get_stock(self):
        return self.stock
        

    def get_shares(self):
        return self.shares
    

    def get_pr_crisis(self):
        return self.pr_crisis
    

    def get_pr_response(self):
        return self.pr_response
    
    
    def get_stock_drop_pr_crisis(self):
        return self.stock_drop_pr_crisis
        
        
    def get_latest_stock_change(self):
        return self.latest_stock_change
        
        
    def get_investors(self):
        return self.investors

    
    def get_investor_shares(self, investor_name):
        try:
            x = self.investors[investor_name]
        except KeyError:
            x = 0
        return x
        
        
    def set_name(self, name):
        self.name = name
    

    def set_owners(self, owners):
        self.owners = owners
    

    def set_location(self, location):
        self.location = location
    
    
    def set_capital(self, capital):
        self.capital = capital
        
        
    def set_stock(self, stock):
        org_stock = self.stock
        self.stock = stock
        self.latest_stock_change = round(self.stock - org_stock, 2)
    
    
    def set_pr_crisis(self, pr_crisis):
        self.pr_crisis = pr_crisis
    
    
    def set_pr_response(self, pr_response):
        self.pr_response = pr_response
        
    
    def set_stock_drop_pr_crisis(self, pr_stock_drop):
        self.stock_drop_pr_crisis = pr_stock_drop
        
        
    def set_latest_stock_change(self,num):
        self.latest_stock_change = num


    def set_investors(self, dict):
        self.investors = dict


    def add_investor(self, company_name, shares):
        self.investors[company_name] = shares
    
    
    def remove_investor(self, company_name):
        try:
            self.investors.pop(company_name)
        except KeyError:
            print('Non existent investor cannot be removed from the investors dictionary')
     
    
    def release_pr_crisis(self, num): 
        if self.pr_crisis != 0 and self.pr_response == 0:
            raise ValueError('PR response must be released for the existing PR crisis')
            
        self.pr_crisis = num
        self.pr_response = 0
        self.stock_drop_pr_crisis = round(constant.PR_CRISIS[num] / 100 * self.stock, 2)
        self.latest_stock_change = round(-1 * self.stock_drop_pr_crisis, 2)
        self.stock = round(self.stock * (100 - constant.PR_CRISIS[num]) / 100, 2) 
    

    def release_pr_response(self, num):
        if num != 0 and self.pr_crisis == 0:
            raise ValueError('PR Response is applicable only if the company has been hit by a PR crisis.')
        elif num != 0 and self.pr_response != 0:
            raise ValueError('A PR Crisis can take only one PR response.')
            
        self.pr_response = num
        self.latest_stock_change = round((constant.PR_RESPONSE[num] / 100 * self.stock_drop_pr_crisis), 2)
        self.stock = round(self.stock + (constant.PR_RESPONSE[num] / 100 * self.stock_drop_pr_crisis), 2)
    
    
    def create_shares(self, investor_name, no_of_shares, price):
        self.investors[investor_name] = no_of_shares
        self.shares += no_of_shares
        self.increase_capital(no_of_shares * price)
        x = self.calculate_new_stock(no_of_shares, price)
        self.set_stock(x)
    

    def transact_shares(self, old_investor_name, new_investor_name, no_of_shares, price):
        try:
            if no_of_shares <= self.investors[old_investor_name]:
                self.investors[old_investor_name] -= no_of_shares
            else:
                raise InvalidTransactionError("Shares to be sold > Shares owned")
        except KeyError:
            raise InvalidTransactionError("Chosen seller has no shares in the company")

        if self.investors[old_investor_name] == 0:
            self.investors.pop(old_investor_name)

        try:
            self.investors[new_investor_name] += no_of_shares
        except KeyError:
            self.investors[new_investor_name] = no_of_shares
        
        x = self.calculate_new_stock(no_of_shares, price)
        self.set_stock(x)
    

    def increase_stock(self, stock_change):
        self.stock += stock_change
        self.latest_stock_change = round(stock_change, 2)
    
    
    def decrease_stock(self, stock_change):
        self.stock -= stock_change
        self.latest_stock_change = round(-1 * stock_change, 2)
    

    def increase_capital(self, money):
        self.capital += money
    
    
    def decrease_capital(self, money):
        self.capital -= money
    

    def calculate_new_stock(self, shares, price):
        value = self.get_stock() * self.get_shares()
        diff = shares * (price - self.get_stock())
        new_value = value + diff
        return round(new_value / self.get_shares(), 2)

