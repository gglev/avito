from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import hashlib
import json


@dataclass
class Price:
    # class for presentation price with support of valutes
    amount: int
    currncy: str = "RUB"
    is_negotiable: bool = False
    original_text: str = ""

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"Price cannot be negative: {self.amount}")
        
    def is_within_range(self, min_price: int, max_price: int) -> bool:
        return min_price <= self.amount <= max_price
    
    def discounted_price(self, discount_percent: float) -> 'Price':
        if not 0 <= discount_percent <= 100:
            raise ValueError("Sale must be from 0 to 100")
        
        new_amount = int(self.amount * (100-discount_percent) / 100)
        return Price(
            amount = new_amount,
            currency = self.currency,
            is_negotiable = self.is_negotiable
        )
    
    def __str__(self) -> str:
        base = f"{self.amount}{self.currency}"
        if self.is_negotiable:
            base += "(negotiable)"
        return base
    
    def __repr__(self) -> str:
        return f"Price(amount={self.amount}, currency={self.currency}, negotiable={self.is_negotiable})"
    
@dataclass
class BookListing:
    """
    Основная сущность - объявление о продаже книги.
    
    Attributes:
        id: Уникальный идентификатор (хэш от URL)
        title: Название книги
        description: Описание из объявления
        price: Объект Price с ценой
        url: Ссылка на объявление
        images: Список URL изображений
        created_at: Дата создания объявления
        parsed_at: Дата парсинга
        author: Извлеченный автор (если удалось определить)
        year: Год издания (если указан)
        publisher: Издательство (если указано)
        condition: Состояние (если указано)
        series: Серия книг (если указана)
        is_illustrated: Наличие иллюстраций
        page_count: Количество страниц
        metadata: Дополнительные метаданные
    """
    id: str
    title: str
    description: str
    price: Price
    url: str
    images: List[str]
    created_at: datetime
    parsed_at: Optional[datetime] = None

       # completed at analyze
    author: Optional[str] = None
    year: Optional[str] = None
    publisher: Optional[str] = None
    condition: Optional[str] = None
    series: Optional[str] = None
    is_illustrated: bool = None
    page_count: Optional[str] = None

    metadata: Dict[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        # init after create
        if self.parsed_at is None:
            self.parsed_at = datetime.now()

        # generate id if it not specified
        if not self.id and self.url:
            self.id = hashlib.md5(self.url.encode()).hexdigest()

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        # compare by id
        if not isinstance(other,BookListing):
            return False
        return self.id == other.id
    
    def get_full_text(self) -> str:
        # return text in lower register : name and bio
        return f"{self.title}{self.description}".lower()
    
    def get_short_info(self) -> str:
        # short info about book
        # return str like "name | price in rubles"
        title_short = self.title[:50] + "..." if len(self.title) > 50 else self.title
        return f"{title_short} | {self.price.amount} руб"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': {
                'amount': self.price.amount,
                'currency': self.price.currency,
                'is_negotiable': self.price.is_negotiable
            },
            'url': self.url,
            'images': self.images,
            'created_at': self.created_at.isoformat(),
            'parsed_at': self.parsed_at.isoformat(),
            'author': self.author,
            'year': self.year,
            'publisher': self.publisher,
            'condition': self.condition,
            'series': self.series,
            'is_illustrated': self.is_illustrated,
            'page_count': self.page_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookListing':
        # make an object from dict
        price_data = data.get('price',{})
        price = Price(
            price_data  = data.get('amount', 0),
            currency = price_data.get('currency','RUB'),
            is_negotiable = price_data.get('is_negotiable',False)
        )
        
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        parsed_at = datetime.fromisoformat(data['parsed_at']) if 'parsed_at' not in data else None

        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            price=price,
            url=data['url'],
            images=data.get('images', []),
            created_at=created_at,
            parsed_at=parsed_at,
            author=data.get('author'),
            year=data.get('year'),
            publisher=data.get('publisher'),
            condition=data.get('condition'),
            series=data.get('series'),
            is_illustrated=data.get('is_illustrated', False),
            page_count=data.get('page_count'),
            metadata=data.get('metadata', {})
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent = 2)

    def __str__(self) -> str:
        return f"{self.title} | {self.prce} | {self.url}"

    def __repr__(self) -> str:
        return f"BookListing(id='{self.id[:8]}', title='{self.title[:30]}...', price={self.price.amount})"

@dataclass
class AnalysisResult:
    """
    Результат анализа книги.
    
    Attributes:
        listing: Исходное объявление
        score: Общая оценка (0-1)
        is_match: Подходит ли книга под критерии
        reasons: Список причин, почему книга интересна
        ml_prediction: Предсказание ML модели (если есть)
        image_scores: Оценки по каждому фото
        text_score: Оценка текста
        price_score: Оценка цены
        condition_score: Оценка состояния
        rare_score: Оценка редкости
        details: Детальная информация по каждому критерию
    """
    listing: BookListing
    score: float
    is_match: bool
    reasons: List[str]
    
    # optional
    ml_prediction: Optional[float] = None
    image_scores: Optional[List[float]] = None
    text_score: Optional[float] = None
    price_score: Optional[float] = None
    condition_score: Optional[float] = None
    rare_score: Optional[float] = None
    
    #detalization
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not 0 <= self.score <= 1:
            raise ValueError(f"Score должен быть от 0 до 1, получено {self.score}")
    
    @property
    def is_excellent(self) -> bool:
        return self.score > 0.8
    
    @property
    def is_good(self) -> bool:
        return self.score > 0.6
    
    @property
    def summary(self) -> str:
        return f"Score: {self.score:.2f} | Причин: {len(self.reasons)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'is_match': self.is_match,
            'reasons': self.reasons,
            'ml_prediction': self.ml_prediction,
            'text_score': self.text_score,
            'price_score': self.price_score,
            'condition_score': self.condition_score,
            'rare_score': self.rare_score,
            'details': self.details,
            'listing_id': self.listing.id,
            'listing_title': self.listing.title
        }
    
    def __str__(self) -> str:
        return self.summary