import requests
from bs4 import BeautifulSoup
from app.database import SessionLocal
from app.models import Book


def scrape_books():
    url = "https://books.toscrape.com/catalogue/page-1.html"
    session = SessionLocal()

    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar {url}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        bookshelf = soup.find_all("li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"})
        for book in bookshelf:
            title = book.h3.a["title"]
            price_text = book.find("p", class_="price_color").text
            price_clean = price_text.replace("£", "").replace("Â", "").strip()
            price = float(price_clean)
            availability = book.find("p", class_="instock availability").get_text(strip=True)
            rating = book.find("p", class_="star-rating")["class"][1]
            ratings_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            rating_value = ratings_map.get(rating, None)
            img_url = "https://books.toscrape.com/" + book.find("img")["src"].replace("../", "")
            #Para pegar a categoria 
            book_url = "https://books.toscrape.com/catalogue/" + book.h3.a["href"]
            book_resp = requests.get(book_url)
            book_soup = BeautifulSoup(book_resp.text, "html.parser")
            category = book_soup.find("ul", class_="breadcrumb").find_all("a")[2].get_text(strip=True)

            new_book = Book(
                titulo=title,
                preco=float(price),
                disponibilidade=availability,
                rating=rating_value,
                categoria=category,
                imagem=img_url
            )
            session.add(new_book)

        print(f"Página processada: {url}")

        # Pega link da próxima página
        next_page = soup.select_one("li.next a")
        if next_page:
            next_url = next_page["href"]
            # Constrói a URL completa
            if "catalogue/" not in next_url:
                url = "https://books.toscrape.com/catalogue/" + next_url
            else:
                url = "https://books.toscrape.com/" + next_url
        else:
            url = None

    session.commit()
    session.close()
    print("Todos os livros foram salvos no banco")

if __name__ == "__main__":
    scrape_books()


