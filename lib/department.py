from __init__ import CONN, CURSOR


class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name         # validated via setter
        self.location = location # validated via setter

    # ---------- Properties with Validation ----------

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Department name must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Department name must be a non-empty string.")
        self._name = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("Department location must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Department location must be a non-empty string.")
        self._location = value

    # ---------- Class/Table Methods ----------

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    @classmethod
    def instance_from_db(cls, row):
        if row:
            id, name, location = row
            if id in cls.all:
                return cls.all[id]
            instance = cls(name, location, id)
            cls.all[id] = instance
            return instance

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # ---------- Instance Methods ----------

    def save(self):
        if self.id is None:
            sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
            CURSOR.execute(sql, (self.name, self.location))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Department.all[self.id] = self
        else:
            self.update()

    def update(self):
        sql = "UPDATE departments SET name = ?, location = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Department.all:
            del Department.all[self.id]
        self.id = None

    def employees(self):
        from employee import Employee  # late import to avoid circular dependency
        sql = "SELECT * FROM employees WHERE department_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows]
