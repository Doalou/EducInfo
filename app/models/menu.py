"""Menu de cantine et catégories partagées."""

from app.extensions import db

MENU_CATEGORIES = {
    1: {"label": "Entrée", "icon": "🥗"},
    2: {"label": "Plat principal", "icon": "🍲"},
    3: {"label": "Accompagnement", "icon": "🥔"},
    4: {"label": "Fromage", "icon": "🧀"},
    5: {"label": "Dessert", "icon": "🍎"},
}


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    icons = db.Column(db.String(32), nullable=False, default="")
    date = db.Column(db.Date, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.CheckConstraint("category BETWEEN 1 AND 5", name="valid_menu_category"),
        db.Index("idx_menu_date_category", "date", "category", "order"),
    )

    @property
    def category_label(self) -> str:
        return MENU_CATEGORIES[self.category]["label"]

    @property
    def category_icon(self) -> str:
        return MENU_CATEGORIES[self.category]["icon"]

    @classmethod
    def for_date(cls, target: date):
        return cls.query.filter_by(date=target).order_by(cls.category, cls.order, cls.id).all()

    def __repr__(self) -> str:
        return f"<MenuItem {self.date} {self.category_label}: {self.name}>"
