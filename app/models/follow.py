from app.utils.persistence_manager import PersistenceManager
from bson import ObjectId

class Follow:
    # Spotify_Id_1 is the user who is following
    # Spotify_Id_2 is the user who is being followed
    def __init__(self, spotify_id_1, spotify_id_2):
        self.spotify_id_1 = spotify_id_1
        self.spotify_id_2 = spotify_id_2

    def save(self):
        db = PersistenceManager.get_database()
        result = db.follow.insert_one({"spotifyId1": self.spotify_id_1, "spotifyId2": self.spotify_id_2})
        return result.inserted_id
    
    def delete(spotify_id_1, spotify_id_2):
        db = PersistenceManager.get_database()
        result = db.follow.delete_one({"spotifyId1": spotify_id_1, "spotifyId2": spotify_id_2})
        return result.deleted_count > 0
    
    # Get who a person follows, so the spotifyId parameter must be in spotifyId1
    def get_following(spotifyId):
        db = PersistenceManager.get_database()
        following = list(db.follow.find({"spotifyId1": spotifyId}))
        for follow in following:
            follow["_id"] = str(follow["_id"])
        return following
    
    # Get who follows a person, so the spotifyId parameter must be in spotifyId2
    def get_followers(spotifyId):
        db = PersistenceManager.get_database()
        followers = list(db.follow.find({"spotifyId2": spotifyId}))
        for follower in followers:
            follower["_id"] = str(follower["_id"])
        return followers