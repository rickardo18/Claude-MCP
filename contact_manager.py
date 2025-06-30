import json
import os
import re
import csv

class Contact:
    def __init__(self, name, phone, email=None, favourite=False):
        self.name = name
        self.phone = phone
        self.email = email
        self.favourite = favourite

    def to_dict(self):
        return {"name": self.name, "phone": self.phone, "email": self.email}

    @staticmethod
    def from_dict(data):
        return Contact(data["name"], data["phone"], data.get("email"))

    def __str__(self):
        contact_str = f"{self.name} - {self.phone}"
        if self.email:
            contact_str += f" - {self.email}"
        return contact_str

    @staticmethod
    def validate_email(email):
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

class ContactBook:
    def __init__(self, filename="contacts.json"):
        self.contacts = []
        self.filename = filename
        self.load_contacts()

    def add_contact(self, name, phone, email=None):
        if email and not Contact.validate_email(email):
            print("Invalid email format. Contact not added.")
            return
        self.contacts.append(Contact(name, phone, email))
        print(f"Added contact: {name}")
        self.save_contacts()

    def list_contacts(self):
        if not self.contacts:
            print("No contacts found.")
        for idx, contact in enumerate(self.contacts, 1):
            print(f"{idx}. {contact}")

    def find_contact(self, query):
        matches = [c for c in self.contacts if 
                  query.lower() in c.name.lower() or 
                  (c.email and query.lower() in c.email.lower())]
        if matches:
            for c in matches:
                print(c)
        else:
            print("No matching contact found.")

    def remove_contact(self, index):
        try:
            removed = self.contacts.pop(index - 1)
            print(f"Removed: {removed.name}")
            self.save_contacts()
        except IndexError:
            print("Invalid index.")

    def edit_contact(self, index):
        try:
            contact = self.contacts[index - 1]
            print(f"Editing contact: {contact}")
            new_name = input(f"New name (press Enter to keep '{contact.name}'): ").strip()
            new_phone = input(f"New phone (press Enter to keep '{contact.phone}'): ").strip()
            new_email = input(f"New email (press Enter to keep '{contact.email or ''}'): ").strip()
            if new_name:
                contact.name = new_name
            if new_phone:
                contact.phone = new_phone
            if new_email:
                if Contact.validate_email(new_email):
                    contact.email = new_email
                else:
                    print("Invalid email format. Email not updated.")
            elif new_email == '':
                contact.email = None
            self.save_contacts()
            print("Contact updated.")
        except IndexError:
            print("Invalid index.")

    def save_contacts(self):
        with open(self.filename, "w") as f:
            json.dump([c.to_dict() for c in self.contacts], f, indent=4)

    def load_contacts(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.contacts = [Contact.from_dict(d) for d in data]

    def export_contacts_csv(self, filename="contacts_export.csv"):
        pass

    def list_favourites(self):
        pass

    def mark_favourite(self, index):
        pass

    def unmark_favourite(self, index):
        pass

    def import_contacts_csv(self, filename="contacts_import.csv"):
        if not os.path.exists(filename):
            print(f"File '{filename}' not found.")
            return
        added = 0
        skipped = 0
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get('name', '').strip()
                phone = row.get('phone', '').strip()
                email = row.get('email', '').strip() or None
                if not name or not phone:
                    print(f"Skipping row with missing name or phone: {row}")
                    skipped += 1
                    continue
                # Duplicate check (same as add_contact)
                duplicate = False
                for c in self.contacts:
                    if (c.name.lower() == name.lower() and (c.phone == phone or (email and c.email and c.email.lower() == email.lower()))):
                        duplicate = True
                        break
                if duplicate:
                    print(f"Duplicate contact skipped: {name}")
                    skipped += 1
                    continue
                if email and not Contact.validate_email(email):
                    print(f"Invalid email for {name}, skipping.")
                    skipped += 1
                    continue
                self.contacts.append(Contact(name, phone, email))
                added += 1
        self.save_contacts()
        print(f"Import complete. {added} contacts added, {skipped} skipped.")

def main():
    book = ContactBook()
    while True:
        print("\nCommands: add, list, find, remove, edit, exit")
        cmd = input("Enter command: ").strip().lower()

        if cmd == "add":
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email (optional, press Enter to skip): ").strip() or None
            book.add_contact(name, phone, email)
        elif cmd == "list":
            book.list_contacts()
        elif cmd == "find":
            query = input("Search by name or email: ")
            book.find_contact(query)
        elif cmd == "remove":
            index = int(input("Contact number to remove: "))
            book.remove_contact(index)
        elif cmd == "edit":
            index = int(input("Contact number to edit: "))
            book.edit_contact(index)
        elif cmd == "exit":
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
