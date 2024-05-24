from models import User, Picture, session

def test_create_user():
    new_user = User(name="John Doe", email="john@example.com", password="secret")
    session.add(new_user)
    session.commit()
    assert new_user.id is not None
    session.delete(new_user)
    session.commit()

def test_query_user():
    new_user = User(name="Jane Doe", email="jane@example.com", password="secret")
    session.add(new_user)
    session.commit()

    queried_user = session.query(User).filter_by(email="jane@example.com").first()
    assert queried_user is not None
    assert queried_user.name == "Jane Doe"
    session.delete(new_user)
    session.commit()

def test_create_picture():
    user = User(name="Alice", email="alice@example.com", password="secret")
    session.add(user)
    session.commit()

    new_picture = Picture(path="/images/alice.jpg", name="Alice's Picture", user_id=user.id)
    session.add(new_picture)
    session.commit()
    assert new_picture.id is not None
    session.delete(new_picture)
    session.delete(user)
    session.commit()

def test_query_picture():
    user = User(name="Bob", email="bob@example.com", password="secret")
    session.add(user)
    session.commit()

    new_picture = Picture(path="/images/bob.jpg", name="Bob's Picture", user_id=user.id)
    session.add(new_picture)
    session.commit()

    queried_picture = session.query(Picture).filter_by(name="Bob's Picture").first()
    assert queried_picture is not None
    assert queried_picture.user_id == user.id
    session.delete(new_picture)
    session.delete(user)
    session.commit()

def test_delete_user():
    new_user = User(name="Charlie", email="charlie@example.com", password="secret")
    session.add(new_user)
    session.commit()

    session.delete(new_user)
    session.commit()

    deleted_user = session.query(User).filter_by(email="charlie@example.com").first()
    assert deleted_user is None

def test_delete_picture():
    user = User(name="Dave", email="dave@example.com", password="secret")
    session.add(user)
    session.commit()

    new_picture = Picture(path="/images/dave.jpg", name="Dave's Picture", user_id=user.id)
    session.add(new_picture)
    session.commit()

    session.delete(new_picture)
    session.commit()

    deleted_picture = session.query(Picture).filter_by(name="Dave's Picture").first()
    assert deleted_picture is None
    session.delete(user)
    session.commit()

