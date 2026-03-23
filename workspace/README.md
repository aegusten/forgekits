# Workspace

Drop your project spec files here.

## Usage
1. Create a markdown file describing what you want to build
2. Run: `forgekits --from workspace/your-spec.md`

## Spec File Format
Just describe what you want in plain English:

```markdown
# My Project

Build a REST API for managing a bookstore.

## Requirements
- Books have: title, author, ISBN, price, stock count
- Users can browse, search, and filter books
- Admin users can add/update/delete books
- Authentication with JWT
- PostgreSQL database
```

The more detail you provide, the better the output.
