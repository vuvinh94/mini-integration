-- 1. Top 10 cuốn sách có doanh thu ước tính cao nhất (current_price * quantity)
SELECT
    title,
    authors,
    category,
    current_price,
    quantity,
    ROUND((current_price * quantity)::numeric, 0) AS estimated_revenue
FROM books
WHERE quantity IS NOT NULL
ORDER BY estimated_revenue DESC
LIMIT 10;

-- 2. Thống kê theo thể loại sách (số lượng sách, giá trung bình, tổng lượng bán)
SELECT
    category,
    COUNT(*) AS total_books,
    ROUND(AVG(current_price)::numeric, 0) AS avg_price,
    ROUND(AVG(avg_rating)::numeric, 2) AS avg_rating,
    SUM(quantity) AS total_sold
FROM books
GROUP BY category
HAVING COUNT(*) >= 5
ORDER BY total_sold DESC NULLS LAST;

-- 3. Top 10 nhà xuất bản / nhà phát hành (manufacturer) có nhiều sách bán chạy nhất
SELECT
    manufacturer,
    COUNT(*) AS total_titles,
    SUM(quantity) AS total_sold,
    ROUND(AVG(avg_rating)::numeric, 2) AS avg_rating
FROM books
WHERE manufacturer IS NOT NULL
GROUP BY manufacturer
ORDER BY total_sold DESC NULLS LAST
LIMIT 10;

-- 4. Phân bố điểm đánh giá bình luận (rating distribution)
SELECT
    rating,
    COUNT(*) AS total_comments,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    SUM(thank_count) AS total_thanks
FROM comments
GROUP BY rating
ORDER BY rating DESC;

-- 5. Top 10 cuốn sách được giảm giá sâu nhất (tỷ lệ discount_percent cao nhất)
SELECT
    title,
    authors,
    original_price,
    current_price,
    discount_percent,
    quantity
FROM books
WHERE discount_percent > 0 AND original_price > 0
ORDER BY discount_percent DESC
LIMIT 10;
