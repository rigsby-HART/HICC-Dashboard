import pdb

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from PrepareTables import PrepareTables


class DBUploader:
    def __init__(self, master_data_filepath, db_path):
        self.master_data_filepath = master_data_filepath
        self.db_path = db_path
        
        self.engine = create_engine('sqlite:///' + self.db_path)
        self.pt = PrepareTables(master_data_filepath)
        self.db_base = declarative_base()
        self.upload_tables()
        self.Session = sessionmaker(bind=self.engine)

    def __call__(self):

        
        # Preparing Outputs
        self.insert_data(self.output_2, self.Output_2)
        self.insert_data(self.output_3, self.Output_3)
        self.insert_data(self.output_4a, self.Output_4a)
        self.insert_data(self.output_4b, self.Output_4b)
        self.insert_data(self.output_5a_new, self.Output_5a)
        self.insert_data(self.output_5b, self.Output_5b)
        self.insert_data(self.output_6, self.Output_6)
        self.insert_data(self.output_7, self.Output_7)
        self.insert_data(self.output_8, self.Output_8)
        self.insert_data(self.output_9, self.Output_9)
        self.insert_data(self.output_10a, self.Output_10a)
        self.insert_data(self.output_10b, self.Output_10b)

        

        print('Database ready....')


    def upload_tables(self):

        class Output_2(self.db_base):
            __tablename__ = "output_2"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_2 = Output_2  # Assign the class

        # Fetch and store data
        self.output_2 = self.pt.prepare_output_2()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_2, self.output_2, 'Metric')


        class Output_3(self.db_base):
            __tablename__ = "output_3"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_3 = Output_3  # Assign the class

        # Fetch and store data
        self.output_3 = self.pt.prepare_output_3()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_3, self.output_3, 'Metric')


        class Output_4a(self.db_base):
            __tablename__ = "output_4a"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_4a = Output_4a  # Assign the class

        # Fetch and store data
        self.output_4a = self.pt.prepare_output_4a()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_4a, self.output_4a, 'Metric')

        class Output_4b(self.db_base):
            __tablename__ = "output_4b"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_4b = Output_4b  # Assign the class

        # Fetch and store data
        self.output_4b = self.pt.prepare_output_4b()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_4b, self.output_4b, 'Metric')


        class Output_5a(self.db_base):
            __tablename__ = "output_5a"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_5a = Output_5a  # Assign the class

        # Fetch and store data
        self.output_5a = self.pt.prepare_output_5a()  # Ensure this returns a DataFrame
        self.output_5a_new = self.output_5a.copy()
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_5a, self.output_5a_new, 'Metric')

        
        class Output_5b(self.db_base):
            __tablename__ = "output_5b"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_5b = Output_5b  # Assign the class

        # Fetch and store data
        self.output_5b = self.pt.prepare_output_5b(self.output_5a)  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_5b, self.output_5b, 'Metric')

        class Output_6(self.db_base):
            __tablename__ = "output_6"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_6 = Output_6  # Assign the class

        # Fetch and store data
        self.output_6 = self.pt.prepare_output_6()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_6, self.output_6, 'Metric')


        class Output_7(self.db_base):
            __tablename__ = "output_7"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_7 = Output_7  # Assign the class

        # Fetch and store data
        self.output_7 = self.pt.prepare_output_7()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_7, self.output_7, 'Metric')



        class Output_8(self.db_base):
            __tablename__ = "output_8"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_8 = Output_8  # Assign the class

        # Fetch and store data
        self.output_8 = self.pt.prepare_output_8()  # Ensure this returns a DataFrame
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_8, self.output_8, 'Metric')


        class Output_9(self.db_base):
            __tablename__ = "output_9"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_9 = Output_9  # Assign the class

        # Fetch and store data
        self.output_9, _, _ = self.pt.prepare_output_9_and_10()  # Ensure this returns a DataFrame
        self.output_9.reset_index(inplace=True)
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_9, self.output_9, 'Age')


        class Output_10a(self.db_base):
            __tablename__ = "output_10a"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_10a = Output_10a  # Assign the class

        # Fetch and store data
        _, self.output_10a, _ = self.pt.prepare_output_9_and_10()  # Ensure this returns a DataFrame
        self.output_10a.reset_index(inplace=True)
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_10a, self.output_10a, 'Age')



        class Output_10b(self.db_base):
            __tablename__ = "output_10b"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_10b = Output_10b  # Assign the class

        # Fetch and store data
        _, _, self.output_10b = self.pt.prepare_output_9_and_10()  # Ensure this returns a DataFrame
        self.output_10b.reset_index(inplace=True)
        
        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_10b, self.output_10b, 'Age')



        # Create all tables
        self.db_base.metadata.create_all(self.engine)



    def add_dynamic_columns(self, cls, df, variable_column):
        df = df.replace('--', np.nan)
        df.columns = df.columns.map(str)
        # Dynamically add columns based on the DataFrame columns
        for col in df.columns:
            if col in {'Geography', 'GEO_TYPE_ABBR_EN', f'{variable_column}', 'ALT_GEO_CODE_EN', 'PR_CODE_EN'}:
                setattr(cls, col, Column(String))
            else:
                setattr(cls, col, Column(Float)) 

    def insert_data(self, df, PartnerClass):
        # Create a new session
        session = self.Session()
        records = []
        df = df.replace('--', np.nan)
        # Iterate through the DataFrame and insert data
        try:
            for idx, row in df.iterrows():
                data = {str(k): v for k, v in row.to_dict().items()}
                # print(data)
                records.append(PartnerClass(**data))

            if records:
                session.bulk_save_objects(records)  # Efficient batch insert
                session.commit()  # Commit transaction
        
        except IntegrityError as e:
            session.rollback()  # Rollback if there's an error
            print(f"IntegrityError: {e}")
    
        except Exception as e:
            session.rollback()
            print(f"Unexpected Error: {e}")
        
        finally:
            session.close()  # Ensure session is closed


