from flask import Blueprint, render_template, request, flash, redirect, url_for,Flask,app,current_app
from flask_login import login_required, current_user
from .models import Category, db,Image,Comment
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home(item_id=None):
    home_items = Category.query.filter_by(category='home').all()
    
    return render_template('home.html', items=home, item_type='home', user=current_user,home_items=home_items)
   
@views.route('/add_comment/<int:item_id>', methods=['POST'])
def add_comment(item_id):
    comment_content = request.form.get('comment')
    address = request.form.get('address')

    item = Category.query.get_or_404(item_id)

    new_comment = Comment(content=comment_content, address=address,  category=item)
    db.session.add(new_comment)


    # Update the stock value for the item
    db.session.commit()

    flash('დაკავშირება წარმატებით', 'success')

    return redirect(url_for('views.item_detail', item_type=item.category, item_id=item_id))



@views.route('/<string:item_type>/<int:item_id>', methods=['GET', 'POST'])
def item_detail(item_type, item_id):
    item_type = item_type.lower()

    item_model = Category
    # Get the item from the database based on item_id
    item = item_model.query.get_or_404(item_id)

    return render_template('details.html', item=item, user=current_user)





@views.route('/search', methods=['GET'])
def searchField():
    search_query = request.args.get('q', '').strip()

    if not search_query:
        return redirect(url_for('views.home'))

    results = []

    results.extend(Category.query.filter(or_(Category.name.ilike(f'%{search_query}%'), Category.description.ilike(f'%{search_query}%'))).all())
   

    return render_template('search.html', search_query=search_query, results=results, user=current_user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}



@views.route('/comments', methods=['GET', 'POST'])
@login_required
def comments():
    if current_user.id != 1:
        flash("You must be an admin to access this page.", 'error')
        return redirect(url_for('views.home'))

    comments_list = Comment.query.all() 


    return render_template('comments.html', user=current_user, items=comments_list)




@views.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if current_user.id != 1:
        flash("You must be an admin to delete comments.", 'error')
        return redirect(url_for('views.home'))

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()

    flash('Comment deleted successfully!', 'success')

    return redirect(url_for('views.comments'))



@views.route('/update_comment/<int:comment_id>', methods=['POST'])
@login_required
def update_comment(comment_id):
    if current_user.id != 1:
        return "Unauthorized", 401

    comment = Comment.query.get_or_404(comment_id)
    status = request.args.get('status')
    value = request.args.get('value')

    if status == 'success':
        comment.success = value == 'true'
    elif status == 'processing':
        comment.processing = value == 'true'

    db.session.commit()

    return "Comment status updated successfully!", 200

@views.route('/update_stock/<int:item_id>', methods=['POST'])
def update_stock(item_id):
    new_stock = int(request.args.get('new_stock'))

    item = Category.query.get_or_404(item_id)
    item.stocks = new_stock

    db.session.commit()

    return "Stock updated successfully!", 200


@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.id != 1:
        flash("You must be an admin to access this page.", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        category = request.form.get('category')
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        image_files = request.files.getlist('files[]')  # or request.files.getlist('images[]')

        # Create a new item
        new_case = Category(name=name, description=description, price=price, category=category)
        db.session.add(new_case)
        db.session.commit()

        # Handle image uploads and associate them with the category
        for image_file in image_files:
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('img', filename).replace('\\', '/')
                image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_path))
                
                # Create and add the new image to the database
                new_image = Image(image_path=image_path, category_id=new_case.id)  # Associate the image with the new_case
                db.session.add(new_image)
                db.session.commit()

        if category == 'home':
            new_case = Category(name=name, description=description, price=price,  category='home')
        elif category == 'phonecase':
            new_case = Category(name=name, description=description, price=price,  category='phonecase')
        elif category == 'protection':
            new_case = Category(name=name, description=description, price=price,  category='protection')
        elif category == 'charger':
            new_case = Category(name=name, description=description, price=price,  category='charger')
        elif category == 'headphone':
            new_case = Category(name=name, description=description, price=price,  category='headphone')
        elif category == 'keyboard':
            new_case = Category(name=name, description=description, price=price,  category='keyboard')
        elif category == 'mouse':
            new_case = Category(name=name, description=description, price=price,  category='mouse')
        elif category == 'others':
            new_case = Category(name=name, description=description, price=price,  category='others')
        else:
            flash('Invalid category selected.', 'error')
            return redirect(url_for('views.admin'))
        
        

    

        # Redirect to the appropriate category page after adding the item
        return redirect(url_for(f'views.{category}'))
    items_list = Category.query.all()
    

    return render_template('admin.html', user=current_user,items=items_list)

@views.route('/delete_item/home/<int:item_id>', methods=['POST'])
@login_required
def delete_home_item(item_id):
    # Check if the current user is an admin (assuming admin has user id 1)
    if current_user.id != 1:
        flash("You must be an admin to delete items.", 'error')
        return redirect(url_for('views.home'))

    # Get the item from the database based on item_id
    item = Category.query.get_or_404(item_id)

    # Delete the item from the database
    db.session.delete(item)
    db.session.commit()

    flash('Item deleted successfully!', 'success')

    # Redirect to the home page after deleting the item
    return redirect(url_for('views.home'))

@views.route('/delete_item/<string:item_type>/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_type, item_id):
    # Check if the current user is an admin (assuming admin has user id 1)
    if current_user.id != 1:
        flash("You must be an admin to delete items.", 'error')
        return redirect(url_for('views.home'))

    # Determine the model based on the item_type (You can modify this based on your actual category names)
    if item_type == 'phonecase':
        item_model = Category
    elif item_type == 'protection':
        item_model = Category
    elif item_type == 'charger':
        item_model = Category
    elif item_type == 'headphone':
        item_model = Category
    elif item_type == 'keyboard':
        item_model = Category
    elif item_type == 'mouse':
        item_model = Category
    elif item_type == 'others':
        item_model = Category
    else:
        flash('Invalid item type.', 'error')
        return redirect(url_for('views.home'))

    # Get the item from the database based on item_id
    item = item_model.query.get_or_404(item_id)

    # Delete the item from the database
    db.session.delete(item)
    db.session.commit()

    flash('Item deleted successfully!', 'success')

    # Redirect to the appropriate category page after deleting the item
    return redirect(url_for(f'views.{item_type}'))


# Phone cases
@views.route('/phonecase')
@views.route('/phonecase/<int:item_id>')
def phonecase(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        phonecase = Category.query.filter_by(category='phonecase').paginate(page, items_per_page, False)
        return render_template('items.html', items=phonecase, item_type='phonecase', user=current_user, pagination=phonecase)    



@views.route('/protection')
@views.route('/protection/<int:item_id>')
def protection(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        protection = Category.query.filter_by(category='protection').paginate(page, items_per_page, False)
        return render_template('items.html', items=protection, item_type='protection', user=current_user, pagination=protection)

# Charger
@views.route('/charger')
@views.route('/charger/<int:item_id>')
def charger(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        charger = Category.query.filter_by(category='charger').paginate(page, items_per_page, False)
        return render_template('items.html', items=charger, item_type='charger', user=current_user, pagination=charger)

# Headphone
@views.route('/headphone')
@views.route('/headphone/<int:item_id>')
def headphone(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        headphone = Category.query.filter_by(category='headphone').paginate(page, items_per_page, False)
        return render_template('items.html', items=headphone, item_type='headphone', user=current_user, pagination=headphone)

# Keyboard
@views.route('/keyboard')
@views.route('/keyboard/<int:item_id>')
def keyboard(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        keyboard = Category.query.filter_by(category='keyboard').paginate(page, items_per_page, False)
        return render_template('items.html', items=keyboard, item_type='keyboard', user=current_user, pagination=keyboard)

# Mouse
@views.route('/mouse')
@views.route('/mouse/<int:item_id>')
def mouse(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        mouse = Category.query.filter_by(category='mouse').paginate(page, items_per_page, False)
        return render_template('items.html', items=mouse, item_type='mouse', user=current_user, pagination=mouse)

# Others
@views.route('/others')
@views.route('/others/<int:item_id>')
def others(item_id=None):
    if item_id:
        item = Category.query.get_or_404(item_id)
        return render_template('details.html', item=item, user=current_user)
    else:
        page = request.args.get('page', 1, type=int)
        items_per_page = 12
        others = Category.query.filter_by(category='others').paginate(page, items_per_page, False)
        return render_template('items.html', items=others, item_type='others', user=current_user, pagination=others)
