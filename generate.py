import json
import csv

class Neo4jGeneration:

    def __init__(self, dataset_name):
        self.input_file_path = ""
        self.output_file_path = ""
        self.dataset_name = dataset_name
        self.config_file_name = "config/config_"+self.dataset_name+".json"
        self.multi_relation_names = set()
        self.compressed_data = [] #by indexes
        self.data = []
        self.query = ''
        self.cat_dic = {}

    def read_config_file(self):

        with open(self.config_file_name) as json_file :
            data = json.load(json_file)

            self.input_file_path = data['input_file_path']
            self.output_file_path = data['output_file_path']

            for file in data['files']:
                self.data = []
                try:
                    self.read_file(file)
                except UnicodeDecodeError:
                    pass


    def read_file(self, file):
        file_name = file['file_name']

        header = []

        with open(self.input_file_path + file_name, encoding='UTF-8') as csv_file :
            csv_reader = csv.reader(csv_file, delimiter=',')
            co = 0

            for row in csv_reader :
                if co == 0 :
                    header = row
                    co += 1
                else :
                    self.data.append(row)
                    co += 1

        self.generate_files(file, header)
        self.generate_query(file, header)


    def generate_files(self, file, header):
        write_header = []
        file_alias = file['file_alias']
        # check_duplicates = file['check_for_duplicates']
        node_name = file['name']
        isNodeFile = file['isNode']
        skip_attr = file['skips']
        indexes = file['indexes']
        skip_indexes = []
        foreign_keys = file['foreign_keys']

        #remove duplicate indexes
        # if check_duplicates:
        #     self.compress_data(indexes, header)
        # else:
        #     self.compressed_data = self.data

        if len(skip_attr) > 0:
            for a in skip_attr:
                skip_indexes.append(header.index(a))

        for i in range(len(header)):
            if i not in skip_indexes:
                write_header.append(header[i])


        #write node file
        if isNodeFile :
            with open(self.output_file_path +file_alias + node_name + ".csv", mode='w', newline='', encoding='UTF-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(write_header)

                for i in range(len(self.data)):
                    row = self.data[i]
                    if len(skip_indexes) > 0:
                        temp = []
                        for j in range(len(row)):
                            if j not in skip_indexes:
                                temp.append(row[j])
                        row = temp

                    writer.writerow(row)


        # write relationship file
        if len(foreign_keys) > 0:
            for f in range(len(foreign_keys)):
                foreign_key = foreign_keys[f]["id"][0]
                local_key = foreign_keys[f]["from_id"][0]
                relationship_type = foreign_keys[f]["name"][0]
                is_type_available = foreign_keys[f]["name"][1]  #when the relationship types available in an attribute
                add_indexes = []
                attributes = foreign_keys[f]["attr"]

                if is_type_available:
                    type_index = header.index(relationship_type)
                    self.multi_relation_names = set()
                    for i in range(len(self.data)):
                        self.multi_relation_names.add(self.data[i][type_index])
                    self.multi_relation_names = list(self.multi_relation_names)

                    # categorize data based on relationship type
                    self.cat_dic = dict.fromkeys(self.multi_relation_names, -1)
                    for i in range(len(self.data)) :
                        arr = self.cat_dic[self.data[i][type_index]]
                        if arr == -1:
                            arr = []
                            arr.append(i)
                            self.cat_dic[self.data[i][type_index]] = arr
                        else:
                            arr.append(i)

                add_indexes.append(header.index(local_key))
                add_indexes.append(header.index(foreign_key))

                rel_header = []
                rel_header.append(local_key)
                rel_header.append(foreign_key)

                if len(attributes) > 0:
                    for att in attributes:
                        add_indexes.append(header.index(att))
                        rel_header.append(att)

                if not is_type_available:

                    with open(self.output_file_path + file_alias + relationship_type +".csv", mode='w', newline='', encoding='UTF-8') as csv_file :
                        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(rel_header)

                        for i in range(len(self.data)) :
                            row = self.data[i]
                            temp = []

                            for j in add_indexes :
                                temp.append(row[j])

                            if temp[1] != '':           #check whether foreign key is available
                                writer.writerow(temp)
                else:
                    for key in self.cat_dic.keys():
                        type_data = self.cat_dic[key]
                        file_name = self.rename_relationship_type(key)

                        with open(self.output_file_path + file_alias + file_name + ".csv", mode='w', newline='', encoding='UTF-8') as csv_file :
                            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            writer.writerow(rel_header)

                            for i in range(len(type_data)):
                                row = self.data[i]
                                temp = []

                                for j in add_indexes :
                                    temp.append(row[j])

                                if temp[1] != '' :      #check whether foreign key is available
                                    writer.writerow(temp)



    def generate_query(self, file, header):
        #LOAD CSV WITH HEADERS FROM 'file:///movie_titles.csv' AS line CREATE(: Movie {id : toInteger(line.id), release_year : date(line.year), name : line.name})
        node_name = file['name']
        file_alias = file['file_alias']
        isNodeFile = file['isNode']
        indexes = file['indexes']
        data_types = file['data_types']
        int_types = data_types[0]['int']
        float_types = data_types[1]['float']
        skip_attr = file['skips']
        foreign_keys = file['foreign_keys']
        skip_attrs = []
        is_numerical_contains = False

        if len(skip_attr) > 0:
            for i in skip_attr:
                skip_attrs.append(i)

        temp = ''
        if isNodeFile:
            if len(int_types) > 0:
                for i in range(len(int_types)):
                    is_numerical_contains = True
                    temp += int_types[i]+':toInteger(line.'+int_types[i]+')'
                    if i is not len(int_types)-1:
                        temp += ','

                    skip_attrs.append(int_types[i])

            if len(float_types) > 0:

                if is_numerical_contains :
                    temp += ','

                for i in range(len(float_types)):
                    is_numerical_contains = True
                    temp += float_types[i]+':toFloat(line.'+float_types[i]+')'
                    if i is not len(float_types)-1:
                        temp += ','

                    skip_attrs.append(float_types[i])

            x = 0
            for i in range(len(header)):

                string_size = len(header) - len(int_types) - len(float_types) - len(skip_attr)

                if header[i] not in skip_attrs:

                    if is_numerical_contains:
                        temp += ','
                        is_numerical_contains = False

                    temp += header[i] + ':line.' + header[i]

                    if x is not string_size-1:
                        temp += ','
                    x += 1

            self.query += "LOAD CSV WITH HEADERS FROM \'file:///"
            self.query += file_alias+ node_name + '.csv\' AS line CREATE(:'+ node_name
            self.query += '{'+ temp +'});\n'

            #Indexes
            if len(indexes) >0:
                temp = ''
                for i in range(len(indexes)) :

                    temp += indexes[i]
                    if i is not len(indexes) - 1 :
                        temp += ','

                index_str = 'CREATE INDEX ON:'+node_name+'('+temp+');\n'
                self.query += index_str
                print(self.query)

        #Relationships
        #LOAD CSV WITH HEADERS FROM "file:///ratings.csv" AS line MATCH(c: Customer {id : toInteger(line.customer_id)}), (m:Movie{id : toInteger(line.movie_id)}) CREATE(c) - [: RATED {rating : toInteger(line.rating), date : apoc.date.parse(line.date, 'mm/dd/yyyy')}]->(m)
        if len(foreign_keys) > 0:
            rel = ''
            for f in range(len(foreign_keys)):

                foreign_key = foreign_keys[f]["id"][0]
                actual_foreign_key = foreign_keys[f]["id"][1]
                local_key = foreign_keys[f]["from_id"][0]
                actual_local_key = foreign_keys[f]["from_id"][1]

                from_table = foreign_keys[f]["from_table"]
                to_table = foreign_keys[f]["to_table"]

                foreign_data_type = foreign_keys[f]["data_type"]
                relationship_type = foreign_keys[f]["name"][0]
                is_type_available = foreign_keys[f]["name"][1]
                attributes = foreign_keys[f]["attr"]

                if local_key in int_types:
                    x1 = 'toInteger(line.'+local_key+')'
                elif local_key in float_types:
                    x1 = 'toFloat(line.' + local_key + ')'
                else:
                    x1 = 'line.' + local_key

                if foreign_data_type == 'int':
                    x2 = 'toInteger(line.'+foreign_key+')'
                elif local_key in float_types:
                    x2 = 'toFloat(line.' + foreign_key + ')'
                else:
                    x2 = 'line.' + foreign_key

                #Todo - only supports for strings
                attr = ''
                if len(attributes) > 0:
                    for i in range(len(attributes)):
                        #rating : toInteger(line.rating)
                        attr +=  attributes[i] + ':line.' + attributes[i]
                        if i is not len(attributes) - 1 :
                            attr += ','

                    attr = '{' +attr+ '}'

                if not is_type_available:
                    rel += 'LOAD CSV WITH HEADERS FROM \'file:///'+file_alias + relationship_type+'.csv\' AS line MATCH(x1:'+from_table+'{'+actual_local_key+':'+x1+'}),(x2:'+to_table+'{'+actual_foreign_key+':'+x2+'}) CREATE(x1)-[:'+relationship_type+attr+']->(x2);\n'
                else:
                    for key in self.cat_dic.keys() :
                        relationship_type = self.rename_relationship_type(key)
                        rel += 'LOAD CSV WITH HEADERS FROM \'file:///' +file_alias + relationship_type + '.csv\' AS line MATCH(x1:' + from_table + '{' + actual_local_key + ':' + x1 + '}),(x2:' + to_table + '{' + actual_foreign_key + ':' + x2 + '}) CREATE(x1)-[:' + relationship_type + attr + ']->(x2);\n'
            print(rel)
            self.query += rel

        self.write_query_file(self.query)

    def write_query_file(self, text):
        file = open("neo4j_insert_queries_"+self.dataset_name+".txt", "w")
        file.write(text)
        file.close()

    def rename_relationship_type(self, name) :

        name = name.replace(' ', '_')
        name = name.replace('/', '_')
        name = name.replace(',', '_')
        name = name.replace('-', '_')
        return name

    def compress_data(self, indexes, header):
        #Todo - implement an efficient code
        index_arr = []
        for i in indexes:
            index_arr.append(header.index(i))

        value_arr = []
        for i in range(len(index_arr)):
            value_arr.append([])

        for x in range(len(self.data)):

            first_index = index_arr[0]
            if self.data[first_index] in value_arr[0]:
                arr_index = value_arr[0].index(self.data[first_index])
                isDuplicate = True
                for i in range(1,len(index_arr)):
                    if self.data[x][index_arr[i]] != value_arr[i][arr_index]:
                        isDuplicate = False
            else:
                isDuplicate = False

            if not isDuplicate:
                for i in range(0, len(index_arr)) :
                    value_arr[i].append(self.data[x][index_arr[i]])

                self.compressed_data.append(self.data[x])


if __name__=="__main__":
    n = Neo4jGeneration("mimic_2")
    n.read_config_file()
