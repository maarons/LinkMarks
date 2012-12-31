from sqlalchemy import Sequence, Column
from sqlalchemy import Integer, String
from sqlalchemy import or_

from model.Base import Base
import model

# Convert tags string to internal representation.
def tags_to_intern(tags):
    return ",".join(map(lambda t: t.strip(), tags.split(",")))

# Inverse of the previous method.
def intern_to_tags(tags):
    return tags.replace(",", ", ")

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(
        Integer,
        Sequence("bookmarks_id_seq"),
        primary_key = True
    )

    name = Column(String, nullable = False)
    url = Column(String, nullable = False)
    keyword = Column(String)
    # Coma delimited list of tags.
    tags = Column(String, nullable = False)

    @staticmethod
    def find_keyword(keyword):
        session = model.Session()
        query = session.query(Bookmark).filter(Bookmark.keyword == keyword)
        try:
            return query.one()
        except:
            # Multiple or no results.
            return None

    @staticmethod
    def find_all(query, count = None):
        like_query = "%{0}%".format(query)
        session = model.Session()
        query = session.query(Bookmark).filter(or_(
            Bookmark.name.like(like_query),
            Bookmark.url.like(like_query),
            Bookmark.tags.like(like_query)
        )).order_by(
            Bookmark.name
        ).order_by(
            Bookmark.id
        )
        if count is not None:
            query = query.limit(count)
        return query.all()

    @staticmethod
    def new(name, url, keyword, tags):
        session = model.Session()
        bookmark = Bookmark()
        bookmark.name = ""
        bookmark.url = ""
        bookmark.tags = ""
        session.add(bookmark)
        session.commit()
        id = bookmark.id
        session.close()
        Bookmark.update(id, name, url, keyword, tags)

    @staticmethod
    def update(id, name, url, keyword, tags):
        bookmark = Bookmark.get(id)
        session = model.Session()
        bookmark.name = name
        bookmark.url = url.strip()
        if keyword:
            bookmark.keyword = keyword
        else:
            bookmark.keyword = None
        bookmark.tags = tags_to_intern(tags)
        session.add(bookmark)
        session.commit()

    @staticmethod
    def get(id):
        session = model.Session()
        bookmark = session.query(Bookmark).filter(Bookmark.id == id).one()
        session.close()
        return bookmark

    @staticmethod
    def delete(id):
        bookmark = Bookmark.get(id)
        session = model.Session()
        session.delete(bookmark)
        session.commit()

    def getTagString(self):
        return intern_to_tags(self.tags)

    def getTagList(self):
        if self.tags:
            return self.tags.split(',')
        else:
            return []

    def getKeyword(self):
        return "" if self.keyword is None else self.keyword

    def search(self, query):
        url = self.url
        if self.keyword is not None:
            query = query[len(self.keyword) + 1:]
            url = url.replace("%s", query)
        return url
