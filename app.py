from neo4j import GraphDatabase

class SocialNetworkApp:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def register_user(self, name, age, location, interests):
        with self.driver.session() as session:
            session.execute_write(self._create_user, name, age, location, interests)

    @staticmethod
    def _create_user(tx, name, age, location, interests):
        tx.run("CREATE (u:User {name: $name, age: $age, location: $location, interests: $interests})",
               name=name, age=age, location=location, interests=interests)
    

    def update_user_info(self, name, age=None, location=None, interests=None):
        with self.driver.session() as session:
            session.execute_write(self._update_user, name, age, location, interests)

    @staticmethod
    def _update_user(tx, name, age, location, interests):
        query = "MATCH (u:User {name: $name}) SET "
        params = {"name": name}
        if age:
            query += "u.age = $age, "
            params["age"] = age
        if location:
            query += "u.location = $location, "
            params["location"] = location
        if interests:
            query += "u.interests = $interests, "
            params["interests"] = interests
        query = query.rstrip(", ")
        tx.run(query, **params)
   
    def send_friend_request(self, from_user, to_user):
        with self.driver.session() as session:
            session.execute_write(self._send_friend_request, from_user, to_user)

    @staticmethod
    def _send_friend_request(tx, from_user, to_user):
        query = (
            "MATCH (from:User {name: $from_user}), (to:User {name: $to_user}) "
            "MERGE (from)-[:OUTGOING_REQUEST]->(to)"
        )
        tx.run(query, from_user=from_user, to_user=to_user)

    def accept_friend_request(self, from_user, to_user):
        with self.driver.session() as session:
            session.execute_write(self._accept_friend_request, from_user, to_user)

    @staticmethod
    def _accept_friend_request(tx, from_user, to_user):
        query = (
            "MATCH (from:User {name: $from_user})-[r:OUTGOING_REQUEST]->(to:User {name: $to_user}) "
            "CREATE (from)-[:FRIENDS_WITH {since: date()}]->(to) "
            "CREATE (to)-[:FRIENDS_WITH {since: date()}]->(from) "
            "DELETE r"
        )
        tx.run(query, from_user=from_user, to_user=to_user)

    def remove_friend(self, user1, user2):
        with self.driver.session() as session:
            session.execute_write(self._delete_friendship, user1, user2)

    @staticmethod
    def _delete_friendship(tx, user1, user2):
        tx.run("MATCH (u1:User {name: $user1})-[f:FRIENDS_WITH]-(u2:User {name: $user2}) DELETE f",
               user1=user1, user2=user2)
        
    def create_post(self, user, content):
        with self.driver.session() as session:
            session.execute_write(self._create_post, user, content)

    @staticmethod
    def _create_post(tx, user, content):
        tx.run("MATCH (u:User {name: $user}) "
               "CREATE (p:Post {content: $content, timestamp: datetime()})-[:POSTED_BY]->(u)",
               user=user, content=content)
        
    def like_post(self, user, post_content):
        with self.driver.session() as session:
            session.execute_write(self._like_post, user, post_content)

    @staticmethod
    def _like_post(tx, user, post_content):
        tx.run("MATCH (u:User {name: $user}), (p:Post {content: $post_content}) "
               "MERGE (u)-[:LIKES]->(p)",
               user=user, post_content=post_content)

    def comment_on_post(self, user, post_content, comment_text):
        with self.driver.session() as session:
            session.execute_write(self._comment_on_post, user, post_content, comment_text)

    @staticmethod
    def _comment_on_post(tx, user, post_content, comment_text):
        tx.run("MATCH (u:User {name: $user}), (p:Post {content: $post_content}) "
               "CREATE (u)-[:COMMENTED_ON {text: $comment_text}]->(p)",
               user=user, post_content=post_content, comment_text=comment_text)

    def create_group(self, name, description):
      with self.driver.session() as session:
        session.execute_write(self._create_group, name, description)

    @staticmethod
    def _create_group(tx, name, description):
        tx.run("CREATE (group:Group {name: $name, description: $description})",
            name=name, description=description)    
        
    def join_group(self, user, group_name):
        with self.driver.session() as session:
            session.execute_write(self._join_group, user, group_name)

    @staticmethod
    def _join_group(tx, user, group_name):
        tx.run("MATCH (u:User {name: $user}), (g:Group {name: $group_name}) "
               "MERGE (u)-[:JOIN {since: date()}]->(g)",
               user=user, group_name=group_name)

    # def recommend_friends(self, user):
    #  with self.driver.session() as session:
    #     result = session.execute_read(self._recommend_friends, user)
    #     return [record["recommended_friend"] for record in result]

    # @staticmethod
    # def _recommend_friends(tx, user):
    #  query = """
    #  MATCH (u:User {name: $user})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(recommended_friend)
    #  WHERE NOT (u)-[:FRIENDS_WITH]->(recommended_friend) AND u <> recommended_friend
    #  RETURN DISTINCT recommended_friend.name AS recommended_friend
    #  """
    #  result = tx.run(query, user=user)
    #  return result
    
    # def search_users(self, name=None, location=None, interests=None):
    #     with self.driver.session() as session:
    #         result = session.execute_write(self._search_users, name, location, interests)
    #         return [record["user"] for record in result]

    # @staticmethod
    # def _search_users(tx, name, location, interests):
    #     query = "MATCH (u:User) WHERE "
    #     conditions = []
    #     params = {}
    #     if name:
    #         conditions.append("u.name CONTAINS $name")
    #         params["name"] = name
    #     if location:
    #         conditions.append("u.location = $location")
    #         params["location"] = location
    #     if interests:
    #         conditions.append("ANY(interest IN u.interests WHERE interest IN $interests)")
    #         params["interests"] = interests
    #     query += " AND ".join(conditions)
    #     return tx.run(query, **params)

     


if __name__ == "__main__":
    app = SocialNetworkApp("bolt://localhost:7687", "neo4j", "12345678")

    # Example usage
    # app.register_user("Liya", 22, "Addis Ababa", ["AI", "Backend Development"])
    # app.register_user("Alex", 25, "New York", ["Frontend Development", "UI/UX"])
    
    # app.update_user_info("Liya", location="New York")

    # app.send_friend_request("Alex", "John")
    # app.accept_friend_request("Alex", "John")
    # app.remove_friend("Liya", "John")
    # app.create_post("Liya", "Hello, this is my first post!")
    # app.like_post("John", "Hello, this is my first post!")
    # app.comment_on_post("John", "Hello, this is my first post!", "Nice post, Liya!")
    # app.create_group("CodeNight", "Join us!")
    # app.join_group("Liya", "CodeNight")
    # recommended_friends = app.recommend_friends("Liya")
    # print("Recommended Friends for Liya:", recommended_friends)
    # search_results = app.search_users(name="Jo", location="New York")
    # print("Search Results:", search_results)

    app.close()