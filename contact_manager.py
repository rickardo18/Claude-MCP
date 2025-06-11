class Contact:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __str__(self):
        return f"{self.name} - {self.phone}"

class ContactBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, name, phone):
        self.contacts.append(Contact(name, phone))
        print(f"Added contact: {name}")

    def list_contacts(self):
        if not self.contacts:
            print("No contacts found.")
        for idx, contact in enumerate(self.contacts, 1):
            print(f"{idx}. {contact}")

    def find_contact(self, name):
        matches = [c for c in self.contacts if name.lower() in c.name.lower()]
        if matches:
            for c in matches:
                print(c)
        else:
            print("No matching contact found.")

    def remove_contact(self, index):
        try:
            removed = self.contacts.pop(index - 1)
            print(f"Removed: {removed.name}")
        except IndexError:
            print("Invalid index.")

def main():
    book = ContactBook()
    while True:
        print("\nCommands: add, list, find, remove, exit")
        cmd = input("Enter command: ").strip().lower()

        if cmd == "add":
            name = input("Name: ")
            phone = input("Phone: ")
            book.add_contact(name, phone)
        elif cmd == "list":
            book.list_contacts()
        elif cmd == "find":
            query = input("Name to search: ")
            book.find_contact(query)
        elif cmd == "remove":
            index = int(input("Contact number to remove: "))
            book.remove_contact(index)
        elif cmd == "exit":
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
