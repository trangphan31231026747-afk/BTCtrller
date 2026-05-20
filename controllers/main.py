from odoo import http
from odoo.http import request


class LibraryController(http.Controller):


    @http.route(
        '/library/books',
        type='http',
        auth='public',
        website=True
    )
    def library_books(self):

        books = request.env['library.book'].sudo().search([
            ('state', '=', 'available')
        ])

        return request.render(
            'library_portal.book_list_template',
            {
                'books': books
            }
        )

    @http.route(
        '/library/book/<int:book_id>',
        type='http',
        auth='public',
        website=True
    )
    def library_book_detail(self, book_id):

        book = request.env['library.book'].sudo().browse(book_id)

        if not book.exists():
            return request.not_found()

        return request.render(
            'library_portal.book_detail_template',
            {
                'book': book
            }
        )

    @http.route(
        '/library/borrow/<int:book_id>',
        type='http',
        auth='public',
        website=True
    )
    def borrow_form(self, book_id):

        book = request.env['library.book'].sudo().browse(book_id)

        if not book.exists():
            return request.not_found()

        return request.render(
            'library_portal.borrow_form_template',
            {
                'book': book
            }
        )

    @http.route(
        '/library/borrow/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def borrow_submit(self, **post):

        name = post.get('name')
        email = post.get('email')
        phone = post.get('phone')
        book_id = post.get('book_id')

        errors = {}

        if not name:
            errors['name'] = 'Name is required'

        if not email or '@' not in email:
            errors['email'] = 'Invalid email'

        book = request.env['library.book'].sudo().browse(int(book_id))

        if not book.exists():
            return request.not_found()

        if errors:
            return request.render(
                'library_portal.borrow_form_template',
                {
                    'book': book,
                    'errors': errors,
                    'values': post
                }
            )

        borrow = request.env['library.borrow.request'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'book_id': book.id
        })

        return request.redirect(
            '/library/borrow/thank-you?id=%s' % borrow.id
        )

    @http.route(
        '/library/borrow/thank-you',
        type='http',
        auth='public',
        website=True
    )
    def borrow_thank_you(self, **kw):

        borrow_id = kw.get('id')

        record = request.env['library.borrow.request'].sudo().browse(int(borrow_id))

        return request.render(
            'library_portal.borrow_thank_you_template',
            {
                'record': record
            }
        )

    @http.route(
        '/api/library/books',
        type='json',
        auth='public'
    )
    def api_library_books(self):

        books = request.env['library.book'].sudo().search([
            ('state', '=', 'available')
        ])

        return [
            {
                'id': b.id,
                'name': b.name,
                'author': b.author,
                'quantity': b.quantity
            }
            for b in books
        ]

    @http.route(
        '/api/library/borrow',
        type='json',
        auth='public'
    )
    def api_library_borrow(self, name, email, phone, book_id):

        book = request.env['library.book'].sudo().browse(int(book_id))

        if not book.exists():
            return {'success': False, 'error': 'Book not found'}

        if book.quantity < 1:
            return {'success': False, 'error': 'Out of stock'}

        req = request.env['library.borrow.request'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'book_id': book.id
        })

        return {
            'success': True,
            'request_id': req.id
        }

    @http.route(
        '/api/library/my-requests',
        type='json',
        auth='user'
    )
    def my_requests(self):

        email = request.env.user.email

        records = request.env['library.borrow.request'].sudo().search([
            ('email', '=', email)
        ])

        return [
            {
                'id': r.id,
                'name': r.name,
                'email': r.email,
                'book_id': r.book_id.id,
                'book_name': r.book_id.name
            }
            for r in records
        ]