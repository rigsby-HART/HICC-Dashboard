import pdb

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from PrepareTables import PrepareTables


class DBUploader:
    def __init__(self, master_data_filepath, transit_filepath, db_path):
        self.master_data_filepath = master_data_filepath
        self.transit_filepath = transit_filepath

        self.cma_data = pd.read_excel(r"..\\sources\\mapdata_simplified\\cma_data_parquet\\2021_CMA.xls")

        self.db_path = db_path
        
        self.engine = create_engine('sqlite:///' + self.db_path)
        self.pt = PrepareTables(master_data_filepath, transit_filepath)
        self.db_base = declarative_base()
        self.upload_tables()
        self.Session = sessionmaker(bind=self.engine)

    def __call__(self):

        
        # Preparing Outputs
        self.insert_data(self.output_1a, self.Output_1a)
        self.insert_data(self.output_1b, self.Output_1b)
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
        self.insert_data(self.output_11, self.Output_11)
        self.insert_data(self.output_12, self.Output_12)
        self.insert_data(self.output_13, self.Output_13)

        self.insert_data(self.cma_data, self.CMA_Data)

        self.insert_data(self.cma_output_14a, self.CMA_Output_14a)
        self.insert_data(self.cma_output_14b, self.CMA_Output_14b)
        self.insert_data(self.cma_output_16, self.CMA_Output_16)

        print('Database ready....')


    def upload_tables(self):

        class CMA_Data(self.db_base):
            __tablename__ = "cma_data"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.CMA_Data = CMA_Data

        # self, cls, df, variable_column, flag=0
        for col in self.cma_data.columns:
                if col in {'LANDAREA', 'SHAPE_Length', 'Shape_Area'}:
                    setattr(self.CMA_Data, col, Column(Float))
                else:
                    setattr(self.CMA_Data, col, Column(String)) 

        class Output_1a(self.db_base):
            __tablename__ = "output_1a"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_1a = Output_1a  # Assign the class

        # Fetch and store data
        self.output_1a = self.pt.prepare_output_1()  # Ensure this returns a DataFrame

        self.add_dynamic_columns(self.Output_1a, self.output_1a, '', 1)


        class Output_1b(self.db_base):
            __tablename__ = "output_1b"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_1b = Output_1b  # Assign the class

        # Fetch and store data
        self.output_1b = self.pt.prepare_output_1('Future')  # Ensure this returns a DataFrame

        self.add_dynamic_columns(self.Output_1b, self.output_1b, '', 1)

        
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

        class Output_11(self.db_base):
            __tablename__ = "output_11"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_11 = Output_11  # Assign the class

        # Fetch and store data
        self.output_11 = self.pt.prepare_output_11()  # Ensure this returns a DataFrame

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_11, self.output_11, 'Metric')

        class Output_12(self.db_base):
            __tablename__ = "output_12"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_12 = Output_12  # Assign the class

        # Fetch and store data
        self.output_12 = self.pt.prepare_output_12()  # Ensure this returns a DataFrame

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_12, self.output_12, 'Metric')

        class Output_13(self.db_base):
            __tablename__ = "output_13"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.Output_13 = Output_13  # Assign the class

        # Fetch and store data
        self.output_13 = self.pt.prepare_output_13()  # Ensure this returns a DataFrame

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.Output_13, self.output_13, 'Metric')


        class CMA_Output_14a(self.db_base):
            __tablename__ = "cma_output_14a"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.CMA_Output_14a = CMA_Output_14a  # Assign the class

        # Fetch and store data
        self.cma_output_14a = self.pt.prepare_cma_output_14a()  # Ensure this returns a DataFrame
        self.cma_output_14a['Metric'] = 'cma_output_14a' # Adding placeholder column

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.CMA_Output_14a, self.cma_output_14a, 'Metric')


        class CMA_Output_14b(self.db_base):
            __tablename__ = "cma_output_14b"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.CMA_Output_14b = CMA_Output_14b  # Assign the class

        # Fetch and store data
        self.cma_output_14b = self.pt.prepare_cma_output_14b()  # Ensure this returns a DataFrame
        self.cma_output_14b['Metric'] = 'cma_output_14b' # Adding placeholder column

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.CMA_Output_14b, self.cma_output_14b, 'Metric')


        class CMA_Output_16(self.db_base):
            __tablename__ = "cma_output_16"
            pk = Column(Integer, primary_key=True, comment='primary key')  # Add Primary Key

        self.CMA_Output_16 = CMA_Output_16  # Assign the class

        # Fetch and store data
        self.cma_output_16 = self.pt.prepare_cma_output_16()  # Ensure this returns a DataFrame
        self.cma_output_16['Metric'] = 'cma_output_16' # Adding placeholder column

        # Dynamically add columns after fetching the DataFrame
        self.add_dynamic_columns(self.CMA_Output_16, self.cma_output_16, 'Metric')


        ##### Create all tables #######################################################################
        self.db_base.metadata.create_all(self.engine)




    def add_dynamic_columns(self, cls, df, variable_column, flag=0):
        df = df.replace('--', np.nan)
        df.columns = df.columns.map(str)
        
        # Dynamically add columns based on the DataFrame columns
        if flag == 0:
            for col in df.columns:
                if col in {'Geography', f'{variable_column}', 'ALT_GEO_CODE_EN',
                           '20% or under of AMHI', '21% to 50% of AMHI', '51% to 80% of AMHI',
                            '81% to 120% of AMHI', '121% and more of AMHI', '20% or under of AMHI.1',
                             '21% to 50% of AMHI.1', '51% to 80% of AMHI.1',
                            '81% to 120% of AMHI.1', '121% and more of AMHI.1'}:
                    setattr(cls, col, Column(String))
                else:
                    setattr(cls, col, Column(Float)) 
        else:
            for col in df.columns:
                if col in {'ALT_GEO_CODE_EN', 'Data', 'Characteristic'}:
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


