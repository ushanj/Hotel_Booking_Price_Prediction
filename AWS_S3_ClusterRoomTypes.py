#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

''' Initialize with default environment variables '''
__name__ = "app"
__module__ = "rezaware"
__package__ = "rezaware"
__app__ = "utils"
__conf_file__ = "app.cfg"
__ini_fname__ = "app.ini"
__log_fname__ = "app.log"


from secrets_1 import access_key,secret_access_key,room_list

''' Load necessary and sufficient python librairies that are used throughout the class'''
try:
    import boto3
    import pandas as pd
    import s3fs

    import os
    import pandas as pd
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('distilbert-base-nli-mean-tokens')

    import re
    import preprocessor as p

    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud

    print("All packages in %s %s %s %s imported successfully!"
          % (__app__,__module__,__package__,__name__))

except Exception as e:
    print("Some in packages in {0} didn't load\n{1}".format(__package__,e))




class App:
    
    ''' The App should initialize and instantiate the mining, wrangler, utils, and visuals
        apps (containers). It will use the app.cfg data to configure the app, define the
        database connection, and establish shared data storage method and paths. 
        
        The instantition should involke the app with setting all the paramters. Thereafter,
        share it as an object with the client. Thereafter, the client can use the object
        directly, without any initialization or instantiation to use the attributes and
        methods.
        
        The class should return instantiated modules with data paths for storing unstructured
        data and logging. 
    '''

    storeMethod = None  # dir, s3bucket,
    dataStore = object
    confData = None
    database = object
    logs = object
    modules = []

    def __init__(self, app_name, module=None, package=None, **kwargs):

        print("Attempt to initializing:",app_name)
        self.__name__ = __name__
        self.__package__ = __package__
        self.confFile = __conf_file__
        self.iniFile = __ini_fname__
        self.config = None
        self.confData = None

        try:
            if not app_name in ['mining','utils','visuals','wrangler']:
                raise ValueError("Invalid app name".format(self.appName))
            self.appName = app_name
            self.module = module
            self.package = package
            self.cwd = os.path.dirname(__file__)
            self.appPath = os.path.join(self.cwd,self.appName)

            global logger
            if not os.path.dirname(os.path.join(self.appPath,"logs/")):
                os.makedirs(os.path.dirname(os.path.join(self.appPath,"logs/")))                
            logger=Logger.get_logger(self.cwd,self.appName,None,None,self.confFile)
            logger.info("%s Initialization complete for %s %s",
                        self.__name__,self.__package__,self.appName)
            print("%s Initialization complete for %s %s"
                  % (self.__name__,self.__package__,self.appName))

        except Exception as e:
            print("{0} app - {1} module - failed to initialize {2} with error:\n{3}".
                  format(self.appName,self.module,self.package,e))
            print(traceback.format_exc())


    def get_ini_data(self) -> list:

        self.confData = Config.set_conf_ini_conf(self.appPath,self.confFile)
        return self.confData


    def make_ini_files(self) -> str:
#         self.get_ini_data()
        self.appPath = os.path.join(self.cwd,self.appName)
        self.ini_file_list = Config.set_conf_ini_conf(
            reza_cwd=self.cwd,
            app_name=self.appName,
            app_path=self.appPath,
            conf_file=self.confFile)
        return self.ini_file_list

    def get_package_logger(self):
        return Logger.get_logger(self.cwd,
                                 self.appName,
                                 self.module,
                                 self.package,
                                 self.iniFile)

    def configure(Config):
        
        config = Config.get_configuration(self.confFile)
        print(config.confFile)
        _conf = Config(self.app)
        _data = DataStore(self.app)
        _dbms = Database(self.app)
        _logs = Logger(self.app)

        return App(conf=_conf, data=_data, dbms=_dbms, logs=_logs)

#     config = Config()
#     logger = Logger()
#     dbConn = DataBase()
#     dataStore = DataStore()

    pass


'''
    *** CLASS CONFIG ***

    Initializes a ConfigParser object for any of the rezaware apps, modules, and packages.
    Makes use of the app.cfg files to generate package-wise app.ini files. Use the config
    object for reading and writing app.ini and app.cfg data.

    Contributor(s):
        * ushan.jayasooriya@colombo.rezgateway.com
        * ushanjayasooriya@gmail.com

'''


################################
s3 = boto3.client('s3')

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id= access_key,
    aws_secret_access_key= secret_access_key
)


def bucket_names():
    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)


def file_names(bucket_name):
    for obj in s3.Bucket(bucket_name).objects.all():
        print(obj)


client = boto3.client('s3')
keys = []

bucket = 'rezgcorp-data-science'
resp = client.list_objects_v2(Bucket = bucket)



def merge_csv():
    
    for i in resp['Contents']:
        print(i['Key'])
    if ('prefix' in i['Key']) & ('.csv' in i['Key']):   # prefix filter
        n = "s3://" + bucket + "/" + i['Key']
    print(n)
    keys.append(n)

    print(keys)
    data = pd.concat([pd.read_csv((k)) for k in keys])
    print(data)
    data.to_csv("final.csv", index = False, encoding = 'utf-8-sig') 


    #use this line if you want to download the file local

    path = "s3://bucket_name/folders/" + "filename.csv"
    data.to_csv(path, index = False, encoding = 'utf-8-sig')



def load_csv(bucket_name):
    # Load csv file directly into python
    obj = s3.Bucket(bucket_name).Object('uploads/merged_rates2.csv').get()
    df = pd.read_csv(obj['Body'], index_col=0)

    # Create a new column with index values
    df[''] = df.index

    #using reset_index() to set index into column
    df=df.reset_index()
    df['search_dt'] = pd.to_datetime(df['search_dt']).dt.date


def cluster_room_types(bucket_name ,file_object ):
    # Load csv file directly into python
    obj = s3.Bucket(bucket_name).Object(file_object).get()
    df = pd.read_csv(obj['Body'], index_col=0)
    
    # Create a new column with index values
    df[''] = df.index

    #using reset_index() to set index into column
    df=df.reset_index()
    
    df['search_dt'] = pd.to_datetime(df['search_dt']).dt.date
    df['checkin_date'] = pd.to_datetime(df['checkin_date']).dt.date
    
    # drop null values
    df= df.dropna()
    
    df['checkin_date'] = pd.to_datetime(df['checkin_date'])
    df['search_dt'] = pd.to_datetime(df['search_dt'])

    df['Date_gap'] = df['checkin_date'] - df['search_dt']
     # remove 'days' in 'Date_gap' column
    df['Date_gap'] = df['Date_gap'].astype(str)
    df["Date_gap"]= df["Date_gap"].replace( r"days","", regex=True)
    
    df=df[df.room_rate != 0]
    df = df.reset_index()

    df1 = df[['room_type']]  
    ####################################
    
    corpus = list(df1['room_type'])
    corpus = corpus
    
    ### CLUSTERING ###
    corpus_embeddings = embedder.encode(corpus)
    corpus_embeddings
    
    num_clusters = 10
    clustering_model = KMeans(n_clusters=num_clusters)
    clustering_model.fit(corpus_embeddings)
    cluster_assignment = clustering_model.labels_
    
    cluster_df = pd.DataFrame(corpus, columns = ['corpus'])
    cluster_df['cluster'] = cluster_assignment
    
    # Merge two Dataframes on index of both the dataframes
    df_new = df.merge(cluster_df, left_index=True, right_index=True)
    df_new=df_new.drop([ 'index', ], axis=1)
    
    df_new['new_room_type'] = ''
    
    for i in range(10):    
        df_new['new_room_type'][df_new["cluster"]==i]=room_list[i]
    
    df_new['room_rate'] = df_new['room_rate'].str.replace(r',', '')
    
    # extracting the week from the date
    df_new['week_no'] = df['checkin_date'].dt.week
    
    # convert string to an integer
    df_new['room_rate'] = df_new['room_rate'].astype(int)
    df_new.head(5)
    
    df_new['room_rate'] = df_new['room_rate'].astype('int')
    df_new.to_csv("merged_rates2_1.csv")
