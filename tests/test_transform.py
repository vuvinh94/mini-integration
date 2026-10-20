import pytest
import pandas as pd
from src.transform import transform_books, transform_comments


@pytest.fixture
def sample_books_raw():
    return pd.DataFrame([
        {
            "title": "Cây Cam Ngọt Của Tôi",
            "authors": "José Mauro",
            "original_price": 108000,
            "current_price": 64800,
            "quantity": 53075.0,
            "catagory": "Tiểu Thuyết",
            "n_review": 11478,
            "avg_rating": 5.0,
            "pages": "244",
            "manufacturer": "NXB Hội Nhà Văn",
            "cover_link": "https://img.tikicdn.com/example1.jpg"
        },
        {
            "title": "Cây Cam Ngọt Của Tôi",
            "authors": "José Mauro",
            "original_price": 108000,
            "current_price": 64800,
            "quantity": 53075.0,
            "catagory": "Tiểu Thuyết",
            "n_review": 11478,
            "avg_rating": 5.0,
            "pages": "244",
            "manufacturer": "NXB Hội Nhà Văn",
            "cover_link": "https://img.tikicdn.com/example1.jpg"
        },
        {
            "title": "Nhà Giả Kim",
            "authors": "Paulo Coelho",
            "original_price": 79000,
            "current_price": 47400,
            "quantity": 24668.0,
            "catagory": "Kinh Điển",
            "n_review": 5131,
            "avg_rating": 4.9,
            "pages": "228",
            "manufacturer": "NXB Hà Nội",
            "cover_link": "https://img.tikicdn.com/example2.jpg"
        },
    ])


@pytest.fixture
def sample_comments_raw():
    return pd.DataFrame([
        {
            "product_id": 74021317,
            "comment_id": 1001,
            "title": "Sách hay",
            "thank_count": 12,
            "customer_id": 9999,
            "rating": 5,
            "content": "Giao hàng nhanh, sách đẹp."
        },
        {
            "product_id": 74021317,
            "comment_id": 1001,  # Duplicate
            "title": "Sách hay",
            "thank_count": 12,
            "customer_id": 9999,
            "rating": 5,
            "content": "Giao hàng nhanh, sách đẹp."
        },
        {
            "product_id": 74021317,
            "comment_id": 1002,
            "title": "Bình thường",
            "thank_count": 0,
            "customer_id": 8888,
            "rating": 3,
            "content": "Nội dung tạm ổn."
        },
    ])


class TestTransformBooks:

    def test_removes_duplicates_and_adds_id(self, sample_books_raw):
        result = transform_books(sample_books_raw)
        assert len(result) == 2
        assert "id" in result.columns
        assert list(result["id"]) == [1, 2]

    def test_renames_catagory_to_category(self, sample_books_raw):
        result = transform_books(sample_books_raw)
        assert "category" in result.columns
        assert "catagory" not in result.columns

    def test_calculates_discount_percent(self, sample_books_raw):
        result = transform_books(sample_books_raw)
        assert "discount_percent" in result.columns
        # (108000 - 64800) / 108000 = 40.0%
        assert result.loc[result["title"] == "Cây Cam Ngọt Của Tôi", "discount_percent"].iloc[0] == 40.0


class TestTransformComments:

    def test_removes_duplicate_comments(self, sample_comments_raw):
        result = transform_comments(sample_comments_raw)
        assert len(result) == 2
        assert set(result["comment_id"]) == {1001, 1002}

    def test_validates_rating_range(self, sample_comments_raw):
        result = transform_comments(sample_comments_raw)
        assert result["rating"].min() >= 1
        assert result["rating"].max() <= 5