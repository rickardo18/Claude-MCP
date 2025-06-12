import json
import os
import re
import csv

class Contact:
    def __init__(self, name, phone, email=None, favourite=False, notes=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.favourite = favourite
        self.notes = notes or []

    def to_dict(self):
        return {"name": self.name, "phone": self.phone, "email": self.email, "favourite": self.favourite, "notes": self.notes}

    @staticmethod
    def from_dict(data):
        return Contact(data["name"], data["phone"], data.get("email"), data.get("favourite", False), data.get("notes", []))

    def __str__(self):
        contact_str = f"{self.name} - {self.phone}"
        if self.email:
            contact_str += f" - {self.email}"
        if self.favourite:
            contact_str += " [favourite]"
        if self.notes:
            contact_str += f" | Notes: {len(self.notes)}"
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
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["name", "phone", "email"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for contact in self.contacts:
                writer.writerow(contact.to_dict())
        print(f"Contacts exported to {filename}")

    def list_favourites(self):
        favourites = [c for c in self.contacts if c.favourite]
        if not favourites:
            print("No favourite contacts found.")
        for idx, contact in enumerate(favourites, 1):
            print(f"{idx}. {contact}")

    def mark_favourite(self, index):
        try:
            contact = self.contacts[index - 1]
            contact.favourite = True
            self.save_contacts()
            print(f"Marked {contact.name} as favourite.")
        except IndexError:
            print("Invalid index.")

    def unmark_favourite(self, index):
        try:
            contact = self.contacts[index - 1]
            contact.favourite = False
            self.save_contacts()
            print(f"Unmarked {contact.name} as favourite.")
        except IndexError:
            print("Invalid index.")

    def add_note(self, index, note):
        try:
            contact = self.contacts[index - 1]
            contact.notes.append(note)
            self.save_contacts()
            print(f"Note added to {contact.name}.")
        except IndexError:
            print("Invalid index.")

    def view_notes(self, index):
        try:
            contact = self.contacts[index - 1]
            if not contact.notes:
                print(f"No notes for {contact.name}.")
            else:
                print(f"Notes for {contact.name}:")
                for idx, note in enumerate(contact.notes, 1):
                    print(f"  {idx}. {note}")
        except IndexError:
            print("Invalid index.")

def main():
    book = ContactBook()
    while True:
        print("\nCommands: add, list, list_favourites, mark_favourite, unmark_favourite, find, remove, edit, export, add_note, view_notes, exit")
        cmd = input("Enter command: ").strip().lower()

        if cmd == "add":
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email (optional, press Enter to skip): ").strip() or None
            book.add_contact(name, phone, email)
        elif cmd == "list":
            book.list_contacts()
        elif cmd == "list_favourites":
            book.list_favourites()
        elif cmd == "mark_favourite":
            index = int(input("Contact number to mark as favourite: "))
            book.mark_favourite(index)
        elif cmd == "unmark_favourite":
            index = int(input("Contact number to unmark as favourite: "))
            book.unmark_favourite(index)
        elif cmd == "find":
            query = input("Search by name or email: ")
            book.find_contact(query)
        elif cmd == "remove":
            index = int(input("Contact number to remove: "))
            book.remove_contact(index)
        elif cmd == "edit":
            index = int(input("Contact number to edit: "))
            book.edit_contact(index)
        elif cmd == "export":
            book.export_contacts_csv()
        elif cmd == "add_note":
            index = int(input("Contact number to add note to: "))
            note = input("Enter note: ").strip()
            if note:
                book.add_note(index, note)
            else:
                print("Note cannot be empty.")
        elif cmd == "view_notes":
            index = int(input("Contact number to view notes: "))
            book.view_notes(index)
        elif cmd == "exit":
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
