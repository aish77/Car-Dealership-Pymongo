import pymongo
import datetime
import csv
import pprint

printer = pprint.PrettyPrinter()

client = pymongo.MongoClient('mongodb://...')
db = client['dealership']

cars = db['cars']
customers = db['customers']
purchases = db['purchases']

# cars.insert_one({
#     'Make': 'Ford',
#     'Model': 'One'
# })

# result = cars.find({})
# for results in result:
#     print(results)

def add_car(make, model, year, engine_hp, msrp):
    document = {
        'Make': make,
        'Model': model,
        'Year': year,
        'Engine HP': engine_hp,
        'MSRP': msrp,
        'Date Added': datetime.datetime.now()
    }

    return cars.insert_one(document)

def add_customer(first_name, last_name, dob):
    document = {
        'First Name': first_name,
        'Last Name': last_name,
        'Date Of Birth': dob,
        'Date Added' : datetime.datetime.now()
    }

    return customers.insert_one(document)

def add_purchase(car_id, customer_id, method):
    document = {
        'Car ID': car_id,
        'Customer ID': customer_id,
        'Method': method,
        'Date': datetime.datetime.now()
    }
    return purchases.insert_one(document)

# car= add_car('Mazda','CX5', 2020, 250, 45000 )  
# customer = add_customer('Aishwary', 'Mahajan', 'April-20-1999')
# purchase = add_purchase(car.inserted_id, customer.inserted_id, 'Cash') 

def add_car_data(filename):
    with open(filename, 'r') as file:
        columns = file.readline().split(',')
        file = csv.reader(file)
        columns_needed = ['Make', 'Model', 'Year', 'Engine HP', 'Vehicle Size', 'Vehicle Style', 'MSRP']
        indexs = list(filter(lambda x: columns[x].strip() in columns_needed , [i for i in range(len(columns))]))
        number_columns = {"MSRP", "Year", "Engine HP"}

        documents = []
        for row in file:
            document = {}
            for count, index in enumerate(indexs):
                data = row[index]
                if columns_needed[count] in number_columns:
                    try:
                        data = float(data)
                    except:
                        continue
                document[columns_needed[count]] = data

            documents.append(document)
        
        cars.insert_many(documents)
        
# add_car_data('data.csv')

# cars.delete_many({})

# query all cars marked as ford
# result = cars.find({'Make': {'$eq': 'Ford'}})
# printer.pprint(list(result))

# count of Ford car
# result = cars.count_documents({'Make': {'$eq': 'Ford'}})
# print(result)

# average price of all cars

result = cars.aggregate([
    {
        '$group': {
            '_id': '$Make',
            'count': {'$sum': 1},
            'average_price': {'$avg': '$MSRP'}

        }
    }

])
printer.pprint(list(result))
result = cars.find({}).sort([('MSRP', -1)]).limit(1)
#printer.pprint(list(result))

# Average price of hondas newer than 2000 by model
result = cars.aggregate([
    {
        '$match': {
            'Make': {'$eq': 'Honda'},
            'Year': {'$gt': 2000}
        }
    },
    {
        '$group': {
            '_id': '$Model',
            'average price': {'$avg': '$MSRP'}
        }
    }
])

def get_customer_info():
    print('type in your info')
    first_name = input('First Name: ')
    last_name = input('Last Name: ')
    return first_name, last_name


first, last = get_customer_info()
customer_and_purchases = list(customers.aggregate([
    {
        '$match': {'First Name': first, 'Last Name': last}
    },
    {
        '$lookup': {
            'from': 'purchases',
            'localField': '_id',
            'foreignField': 'Customer ID',
            'as': 'Purchases'
        }
    }
]))

for i, customer in enumerate(customer_and_purchases):
    print(f"{i+1}. {customer['First Name']} {customer['Last Name']}, {customer['Date Of Birth']}")

selection = input('Select a number for the customer: ')
customer = customer_and_purchases[int(selection) - 1]

print(f'Customer has purchased {len(customer["Purchases"])} cars')
for i, entry in enumerate(customer['Purchases']):
    car_id = entry['Car ID']
    car = cars.find_one({'_id': car_id})
    print(f'{i + 1}. {car}')
