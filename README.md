# To-Do List Manager

This project is a simple command-line To-Do List Manager written in Python. It allows users to:

- View all tasks
- Add new tasks
- Mark tasks as done
- Remove tasks

Tasks are stored in a local JSON file (`todo_list.json`). The application provides a menu-driven interface for easy task management.

# Contact Manager

This project also includes a command-line Contact Manager. It allows users to:

- Add new contacts (with name, phone, and optional email)
- List all contacts
- Find contacts by name or email
- Edit or remove contacts
- Mark/unmark contacts as favourites
- List favourite contacts
- Export contacts to CSV

Contacts are stored in a local JSON file (`contacts.json`). The Contact Manager provides a menu-driven interface for easy contact management.

# AI Prompts Submodule

This project uses an external repository for AI prompt files, included as a Git submodule in the `AI Prompts` directory.

## Cloning with Submodules
When cloning this repository, use the following command to ensure the submodule is included:

```
git clone --recurse-submodules <main-repo-url>
```

If you have already cloned the repository without submodules, run:

```
git submodule update --init --recursive
```

## Updating the AI Prompts Submodule
To update the AI Prompts to the latest version from the external repository:

```
cd "AI Prompts"
git pull origin main
cd ..
git add AI\ Prompts
git commit -m "Update AI Prompts submodule"
```

Replace `<main-repo-url>` with your repository's URL.