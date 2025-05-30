from __init__ import CONN, CURSOR
from department import Department

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    # Name property with validation
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Name cannot be empty.")
        self._name = value

    # Job title property with validation
    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Job title cannot be empty.")
        self._job_title = value

    # Department ID property with validation and FK check
    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer.")
        # Check FK exists in departments table
        CURSOR.execute("SELECT id FROM departments WHERE id = ?", (value,))
        if CURSOR.fetchone() is None:
            raise ValueError(f"Department ID {value} does not exist.")
        self._department_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
                (self.name, self.job_title, self.department_id)
            )
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    def update(self):
        if self.id is None:
            raise ValueError("Cannot update Employee without an ID.")
        CURSOR.execute(
            "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?",
            (self.name, self.job_title, self.department_id, self.id)
        )
        CONN.commit()

    def delete(self):
        if self.id is None:
            return
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        Employee.all.pop(self.id, None)
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        id, name, job_title, department_id = row
        if id in cls.all:
            return cls.all[id]
        employee = cls(name, job_title, department_id, id)
        cls.all[id] = employee
        return employee

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        # Import here to avoid circular import
        from review import Review
        # Return list of Review instances for this employee
        return [review for review in Review.get_all() if review.employee_id == self.id]
