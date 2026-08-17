import uuid
from EmailSender import EmailSender
import os
from dotenv import load_dotenv
import mysql.connector
import pgeocode


dist = pgeocode.GeoDistance('US')

class SQLManager:

    """
    The class that manages all system SQL functions and facilitates the EmailSender class as well.
    SQL Structure:
    DELIVERIES:
        0: start,
        1: end,
        2: depart,
        3: reach,
        4: spots,
        5: name,
        6: phone,
        7: email,
        8: people,
        9: uuid,
        10: uni,
        11: taken,
        12: secret_key,
        13: zip_code
    INDIVIDUALS:
        0: id_num,
        1: name,
        2: email,
        3: phone,
        4: parentid
    """

    def __init__(self):
        load_dotenv()
        self.ES = EmailSender()
        self.db = mysql.connector.connect(
          host=os.getenv("SQL_HOST"),
          user=os.getenv("SQL_USER"),
          password=os.getenv("SQL_PASSWORD"),
          database=os.getenv("SQL_DATABASE")
        )

        self.cursor = self.db.cursor(buffered = True)

    def addDeliv(self, data):
        """
        Inserts a delivery and its data into the system.

        :param data: The delivery data that the user has inputted.
        """

        addCommand = "INSERT INTO DELIVERIES (start, end, depart, reach, spots, name, phone, email, people, uuid, uni, taken, secret_key, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        id = str(uuid.uuid4())
        secret = str(uuid.uuid4())
        deliv = (data['start'], data['dropoff'], data['departure'], data['arrival'], data['spots'], data['name'], data['phone'], data['email'], '', id, data['uni'], 0, secret, data['zip'])
        self.cursor.execute(addCommand, deliv)
        self.db.commit()

        self.ES.addEmail(data['email'], id, secret)

        return id, secret

    def getDeliv(self, uni):
        """
        Gets all available deliveries going to a certain university.

        :param uni: The university that is being queried.
        """

        getCommand = "SELECT * FROM DELIVERIES WHERE uni = '"+uni+"' AND depart > NOW() AND taken < spots"
        self.cursor.execute(getCommand)

        result = []
        for x in self.cursor.fetchall():
            result.append(list(x))

        return result

    def indivDeliv(self, data):
        """
        Inserts a user's reservation into the system.

        :param data: The details of the reservation that the user has inputted.
        """

        indivCommand = "INSERT INTO INDIVIDUALS (id_num, name, email, phone, parentid) VALUES (%s, %s, %s, %s, %s)"
        id = str(uuid.uuid4())

        row = self.getByID(data['parentid'])
        if row == "Not found":
            return False

        selectquery = "SELECT * FROM DELIVERIES WHERE uuid = %s"
        self.cursor.execute(selectquery, (data['parentid'],))
        val = ""

        try:
            val = self.cursor.fetchall()[0][8] + id + ","
        except:
            return False

        deliv = (id, data['name'], data['email'], data['phone'], data['parentid'])
        self.cursor.execute(indivCommand, deliv)
        self.db.commit()

        updatequery = "UPDATE DELIVERIES SET taken = taken + 1 WHERE uuid = %s"
        self.cursor.execute(updatequery, (data['parentid'],))

        setquery = "UPDATE DELIVERIES SET people = %s WHERE uuid = %s"
        self.cursor.execute(setquery, (val, data['parentid']))

        self.db.commit()

        self.ES.addRegister(data['email'], data['parentid'], id)

        return True

    def getByIDProtected(self, id, secret):
        """
        Returns the delivery, if any, that matches the ID and secret key inputted; used
        for functions such as editing and deleting a delivery that require protection.

        :param id: The ID of the delivery.
        :param secret: The private key of the delivery.
        """

        self.cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
        row = self.cursor.fetchone()

        if row:
            if row[12] == secret:
                return row
            else:
                return "Not found"
        else:
            return "Not found"

    def getByID(self, id):
        """
        Returns the delivery, if any, that matches the ID inputted; used for functions such as
        viewing a delivery's information that don't require protection.

        :param id: The ID of the delivery.
        :param secret: The private key of the delivery.
        """

        self.cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
        row = self.cursor.fetchone()

        if row != None:
            print("------- error")
            return [row, id]
        else:
            return "Not found"

    def getIndiv(self, parent, child):
        """
        Returns the reservation, if any, that matches the delivery and reservation ID inputted.

        :param parent: The ID of the delivery when protection is needed, for instance editing/deleting,
        otherwise "bypass" where protection is not needed, for instance internal system functions or simple
        viewing.
        :param child: The ID of the reservation.
        """

        if parent == "bypass":
            self.cursor.execute("SELECT * FROM INDIVIDUALS WHERE id_num = %s", (child,))
            row = self.cursor.fetchone()
            if row:
                return row
            else:
                return "Not found"

        self.cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s AND id_num = %s", (parent, child))
        row = self.cursor.fetchone()

        if row:
            return row
        else:
            return "Not found"

    def auto_clear(self):
        """
        Automatically clears all deliveries which departure time has already passed.
        """

        sql = "SELECT uuid FROM DELIVERIES WHERE reach < NOW()"
        self.cursor.execute(sql)

        results = []
        for row in self.cursor:
            results.append(row)

        for x in results:
            self.cursor.execute("DELETE FROM INDIVIDUALS WHERE parentid = %s", (x[0],))
            self.cursor.execute("DELETE FROM DELIVERIES WHERE uuid = %s", (x[0],))

        self.db.commit()

    def delete(self, id, request_type):
        """
        Deletes a given delivery/reservation from the system.

        :param id: The ID of the delivery/reservation that is being deleted.
        :param request_type: "reservation" if a reservation is being deleted, "delivery" if a delivery
        is being deleted.
        """

        if request_type == "reservation":
            self.cursor.execute("SELECT parentid FROM INDIVIDUALS WHERE id_num = %s", (id,))
            parentid = self.cursor.fetchone()[0]

            row = self.getByID(parentid)
            if row != "Not found":
                row = row[0]
            else:
                return False

            self.cursor.execute("SELECT email FROM INDIVIDUALS WHERE id_num = %s", (id,))
            email = self.cursor.fetchone()[0]

            sql = "DELETE FROM INDIVIDUALS WHERE id_num = '"+id+"'"
            self.cursor.execute(sql)
            self.db.commit()

            sql2 = "UPDATE DELIVERIES SET people = REPLACE(people, '"+id+",', '')"
            self.cursor.execute(sql2)
            self.db.commit()

            updatequery = "UPDATE DELIVERIES SET taken = taken - 1 WHERE uuid = %s"
            self.cursor.execute(updatequery, (parentid,))
            self.db.commit()

            self.ES.indivRemove(email, row)

        else:
            row = self.getByID(id)
            if row != "Not found":
                row = row[0]
            else:
                return False

            self.cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s", (id,))
            results = self.cursor.fetchall()
            for x in results:
                self.ES.removeEmailIndiv(x[2], row)

            self.ES.removeEmail(row[7], row)

            sql = "DELETE FROM DELIVERIES WHERE uuid = '"+id+"'"
            self.cursor.execute(sql)
            self.db.commit()

            sql2 = "DELETE FROM INDIVIDUALS WHERE parentid = '"+id+"'"
            self.cursor.execute(sql2)
            self.db.commit()

        return True

    def editEntry(self, id, request_type, data):
        """
        Edits a given delivery/reservation with the provided information.

        :param id: The ID of the delivery/reservation that is being edited.
        :param request_type: "reservation" if a reservation is being edited, "delivery" if a delivery
        is being edited.
        :param data: The new data of the delivery/reservation.
        """

        email_changed = False
        new_key = ""

        if request_type == "reservation":
            if self.getIndiv("bypass", id) == "Not found":
                return False

            self.cursor.execute("SELECT email FROM INDIVIDUALS WHERE id_num = %s", (id,))
            row = self.cursor.fetchone()
            if row[0] != data['email']:
                email_changed = True

            sql = "UPDATE INDIVIDUALS SET name = %s, email = %s, phone = %s WHERE id_num = %s"
            self.cursor.execute(sql, (data['name'], data['email'], data['phone'], id))
            self.db.commit()

            if email_changed:
                new_key = str(uuid.uuid4())

                sql = "UPDATE INDIVIDUALS SET id_num = %s WHERE id_num = %s"
                self.cursor.execute(sql, (new_key, id))
                self.db.commit()

                sql2 = "UPDATE DELIVERIES SET people = REPLACE(people, '"+id+",', '"+new_key+"')"
                self.cursor.execute(sql2)
                self.db.commit()

            self.cursor.execute("SELECT * FROM INDIVIDUALS WHERE id_num = %s", (new_key,))
            row = self.cursor.fetchone()
            uni = self.getByID(row[4])[0][10]
            self.ES.editReservationEmail(data['email'], row, uni)
        else:
            row = self.getByID(id)
            if row != "Not found":
                row = row[0]
            else:
                return False;

            self.cursor.execute("SELECT email FROM DELIVERIES WHERE uuid = %s", (id,))
            row = self.cursor.fetchone()
            if row[0] != data['email']:
                email_changed = True
                new_key = str(uuid.uuid4())

                sql = "UPDATE DELIVERIES SET secret_key = %s WHERE uuid = %s"
                self.cursor.execute(sql, (new_key, id))
                self.db.commit()

            self.cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
            row = self.cursor.fetchone()
            self.ES.editEmail(row[7], row)

            self.cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s", (id,))
            rows = self.cursor.fetchall()
            for x in rows:
                self.ES.editEmailIndiv(x[2], row, x[0])

            sql = "UPDATE DELIVERIES SET start = %s, end = %s, depart = %s, reach = %s, name = %s, phone = %s, email = %s, zip_code = %s WHERE uuid = %s"
            self.cursor.execute(sql, (data['location'], data['dropoff'], data['departure'], data['arrival'], data['name'], data['phone'], data['email'], data['zip'], id))
            self.db.commit()

        if email_changed:
            return new_key
        else:
            return "No new key"

    def getDelivNarrow(self, uni, zip_code, filter):
        """
        Returns all deliveries to a certain university that lie within a certain distance of
        the user's ZIP code.

        :param uni: The university that is being queried.
        :param zip_code: The user's inputted ZIP code.
        :param filter: The distance around the ZIP code that deliveries should be filtered to,
        in miles
        """

        command = "SELECT * FROM DELIVERIES WHERE uni = '"+uni+"' AND depart > NOW() AND taken < spots"
        self.cursor.execute(command)

        result = []
        for x in self.cursor.fetchall():
            distance_km = dist.query_postal_code(str(x[13])[:5], str(zip_code)[:5])

            if (int(distance_km) / 1.609) <= int(filter):
                result.append(list(x))

        return result

    def getTaken(self, id):
        """
        Gets the number of taken spots for a certain delivery.

        :param id: The ID of the delivery being queried.
        """

        self.cursor.execute("SELECT taken FROM DELIVERIES WHERE uuid = %s", (id,))
        return self.cursor.fetchone()

    def ping(self):
        """
        Pings and reconnects to server in order to protect against idle time shutdowns.
        """

        self.db.ping(reconnect=True, attempts=3, delay=0)

    def addVerify(self, data):
        """
        Adds a new delivery into the pending verification table.
        (CURRENTLY NOT IN USE)

        :param data: The full data of the delivery.
        """

        addVerifyCommand = "INSERT INTO VERIFY (start, end, depart, reach, spots, name, phone, email, people, uuid, uni, taken, secret_key, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        id = str(uuid.uuid4())
        secret = str(uuid.uuid4())

        deliv = (data['start'], data['dropoff'], data['departure'], data['arrival'], data['spots'], data['name'], data['phone'], data['email'], '', id, data['uni'], 0, secret, data['zip'])
        self.cursor.execute(addVerifyCommand, deliv)
        self.db.commit()

        self.ES.verifyEmail(data['email'], id, secret)

        return id, secret