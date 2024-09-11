from __init__ import CURSOR, CONN


class Department:
    all ={}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Department instances """
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the name and location values of the current Department instance.
        Update object id attribute using the primary key value of new row.
        """
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """

        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self# is like saying Department.all,self refers to the class instance itself

    @classmethod
    def create(cls, name, location):
        """ Initialize a new Department instance and save the object to the database """
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Department instance"""
        sql = """
            DELETE FROM departments
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()


    @classmethod
    def instance_from_db(cls,row):#designed  to retieve or create a Department object based on a row from the db 
        """ Return a Department object  having the attribute values from the table row."""
        department=cls.all.get(row[0])#checks if there is an existing department object object in the all 
        if department:#if department is found this block is executed,helps check is the db has been updated
            department.name = row[1]
            department.location = row[2]

        else:
            department = cls(row[1],row[2])#if no department was found then this code is executed with name and location as row[1] and row[2]
            department.id=row[0] # the is of the department is set to row[0]
            cls.all[department.id]= department#the new department is added to the cache cls.all with id as the key
        return department    
    @classmethod
    def get_all(cls):# retrieves all rows from the departments table,converts each row into a department object.returns a list of these Department objects
        """Return a list containing a Department object per row in the table"""
        sql = """
            SELECT *
            FROM departments
        """

        rows = CURSOR.execute(sql).fetchall()# retrieves all rows from the departments table

        return [cls.instance_from_db(row) for row in rows]# creates a list of the Department objects from the rows and returns it
    
    @classmethod#return a single DEPARTMENT
    def find_by_id(cls,id):
        """Return a Department object corresponding to the table row matching the specified primary key"""
        sql ="""
            SELECT * 
            FROM departments
            WHERE id =? 
"""  
        row = CURSOR.execute(sql,(id,)).fetchone()# this query with the id parameter the id value is passed as a tuple (id,) retrieves the fisrt row from the result set beacuse the id is unique
        return cls.instance_from_db(row) if row else None
        #cls.instance_from_db(row) convers tuple to class object  so the if else means if in the departments we find the department with the specific id return it else return NONE
        #instance_from_db(row):   
      #   Takes the row (2, 'Finance', 'Building A, West Wing')
     # Creates a Department object with id=2, name='Finance', and location='Building A, West Wing'.
    # Return Value: Department(id=2, name='Finance', location='Building A, West Wing')
    @classmethod
    def find_by_name(cls,name):# same as find_by_id just that here we are using name
        """Return a Department object corresponding to first table row matching specified name"""
        sql =""" 
            SELECT *
            FROM departments
            WHERE name is ?    
            """
        row = CURSOR.execute(sql,(name,)).fetchone()
        return cls.instance_from_db(row)if row else None
    
    def delete(self):# deletes a row from the departmemst table where id mwatches self.id
        """Delete the table row corresponding to the current Department instance,
    delete the dictionary entry, and reassign id attribute"""
        sql="""
            DELETE FROM departments
            WHERE id =?
        """
        CURSOR.execute(sql,(self.id,))
        CONN.commit()# xommits the transaction to make sure that the deletion is saved in the db
        del type(self).all[self.id]
        self.id = None# resets the current department object to None 
