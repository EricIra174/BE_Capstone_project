# Django Blog - Features Documentation

## Blog Post Management

### Features

1. **Create Posts**
   - Rich text editor for post content
   - Image upload with preview
   - Scheduled publishing
   - Tags and categories
   - Draft mode support

2. **Read Posts**
   - Beautiful, responsive post display
   - Syntax highlighting for code blocks
   - Table of contents for long posts
   - Related posts suggestions
   - Social sharing options

3. **Update Posts**
   - Edit existing posts
   - Update post metadata (title, slug, etc.)
   - Change featured image
   - Update publication date

4. **Delete Posts**
   - Soft delete functionality
   - Confirmation dialog
   - Permission-based access control

### Permissions

- **Anonymous Users**: Can view published posts
- **Authenticated Users**: Can create and manage their own posts
- **Staff Users**: Can manage all posts
- **Superusers**: Full access to all features

### API Endpoints

- `GET /api/posts/` - List all published posts
- `POST /api/posts/` - Create a new post (authenticated)
- `GET /api/posts/<slug>/` - Get post details
- `PUT /api/posts/<slug>/` - Update post (author or admin)
- `DELETE /api/posts/<slug>/` - Delete post (author or admin)

### Testing

To test the blog features:

1. Create a test user:
   ```bash
   python manage.py createsuperuser
   ```

2. Run the development server:
   ```bash
   python manage.py runserver
   ```

3. Access the admin panel at `/admin/` to manage posts
4. Visit `/posts/` to see the blog listing
5. Log in to create and manage your posts

### Dependencies

- Django 4.2+
- Pillow (for image processing)
- django-crispy-forms (for form rendering)
- django-taggit (for tags)
- django-markdownx (for rich text editing)

### Environment Variables

Create a `.env` file with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
MEDIA_ROOT=media
MEDIA_URL=/media/
```

### Deployment

For production deployment, make sure to:

1. Set `DEBUG=False`
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper web server (Nginx + Gunicorn)
4. Configure static and media file serving
5. Set up email backend for password resets

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License

This project is licensed under the MIT License.
