from datetime import datetime, timedelta

from flask import Flask

from models import db, Show, Theatre
from run import app as flask_app


def ensure_classic_movies():
    # Classic movies
    classics = [
        {
            'name': 'Fight Club',
            'tags': 'Movie, Drama, Thriller',
            'rating': 8.8,
            'ticket_price': 250,
            'image': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
            'tmdb_id': 550,
            'overview': 'A depressed man suffering from insomnia meets a strange soap salesman and soon finds himself living in his squalid house after his perfect apartment is destroyed.',
            'runtime': 139,
            'release_date': '1999-10-15',
            'tmdb_rating': 8.4,
        },
        {
            'name': 'The Shawshank Redemption',
            'tags': 'Movie, Drama',
            'rating': 9.3,
            'ticket_price': 300,
            'image': 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg',
            'tmdb_id': 278,
            'overview': 'Imprisoned in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison.',
            'runtime': 142,
            'release_date': '1994-09-23',
            'tmdb_rating': 8.7,
        },
        {
            'name': 'The Godfather',
            'tags': 'Movie, Crime, Drama',
            'rating': 9.2,
            'ticket_price': 300,
            'image': 'https://image.tmdb.org/t/p/w500/e5iVtjkjM30znn86JsvkBYtvEo1.jpg',
            'tmdb_id': 238,
            'overview': 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family.',
            'runtime': 175,
            'release_date': '1972-03-14',
            'tmdb_rating': 8.7,
        },
        {
            'name': 'The Godfather: Part II',
            'tags': 'Movie, Crime, Drama',
            'rating': 9.0,
            'ticket_price': 300,
            'image': 'https://image.tmdb.org/t/p/w500/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg',
            'tmdb_id': 240,
            'overview': 'In the continuing saga of the Corleone crime family, a young Vito Corleone grows up in Sicily and in 1910s New York.',
            'runtime': 202,
            'release_date': '1974-12-20',
            'tmdb_rating': 8.6,
        },
        {
            'name': "Schindler's List",
            'tags': 'Movie, Drama, History',
            'rating': 9.0,
            'ticket_price': 280,
            'image': 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg',
            'tmdb_id': 424,
            'overview': 'The true story of how businessman Oskar Schindler saved over a thousand Jewish lives from the Nazis.',
            'runtime': 195,
            'release_date': '1993-12-15',
            'tmdb_rating': 8.6,
        },
        {
            'name': '12 Angry Men',
            'tags': 'Movie, Drama',
            'rating': 9.0,
            'ticket_price': 250,
            'image': 'https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg',
            'tmdb_id': 389,
            'overview': 'A jury holdout attempts to prevent a miscarriage of justice by forcing his colleagues to reconsider the evidence.',
            'runtime': 96,
            'release_date': '1957-04-10',
            'tmdb_rating': 8.5,
        },
    ]

    # Modern/Trending movies
    modern = [
        {
            'name': 'Dune: Part Two',
            'tags': 'Movie, Sci-Fi, Adventure',
            'rating': 8.0,
            'ticket_price': 400,
            'image': 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',
            'tmdb_id': 1096197,
            'overview': 'Paul Atreides unites with the Fremen to seek revenge against those who destroyed his family, while facing a choice between love and the fate of the universe.',
            'runtime': 166,
            'release_date': '2024-02-27',
            'tmdb_rating': 8.2,
        },
        {
            'name': 'Inside Out 2',
            'tags': 'Movie, Animation, Comedy, Family',
            'rating': 8.3,
            'ticket_price': 350,
            'image': 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg',
            'tmdb_id': 1054588,
            'overview': 'Teenager Riley\'s mind headquarters is undergoing a sudden demolition to make room for something entirely unexpected: new Emotions!',
            'runtime': 97,
            'release_date': '2024-06-11',
            'tmdb_rating': 7.6,
        },
        {
            'name': 'Deadpool & Wolverine',
            'tags': 'Movie, Action, Comedy, Superhero',
            'rating': 7.9,
            'ticket_price': 450,
            'image': 'https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg',
            'tmdb_id': 912908,
            'overview': 'Deadpool is offered a place in the Marvel Cinematic Universe by the Time Variance Authority, but instead recruits a variant of Wolverine to save his universe from extinction.',
            'runtime': 128,
            'release_date': '2024-07-24',
            'tmdb_rating': 7.7,
        },
        {
            'name': 'Wicked',
            'tags': 'Movie, Musical, Fantasy',
            'rating': 8.1,
            'ticket_price': 400,
            'image': 'https://image.tmdb.org/t/p/w500/xDGbZ0JJ3mYaGKy4Nzd9Kph6M9L.jpg',
            'tmdb_id': 1184918,
            'overview': 'Elphaba, a misunderstood young woman because of her green skin, and Glinda, a popular girl, become friends at Shiz University in the Land of Oz.',
            'runtime': 160,
            'release_date': '2024-11-22',
            'tmdb_rating': 7.8,
        },
        {
            'name': 'Oppenheimer',
            'tags': 'Movie, Drama, History, Biography',
            'rating': 8.5,
            'ticket_price': 380,
            'image': 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
            'tmdb_id': 872585,
            'overview': 'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.',
            'runtime': 181,
            'release_date': '2023-07-19',
            'tmdb_rating': 8.1,
        },
        {
            'name': 'Barbie',
            'tags': 'Movie, Comedy, Adventure, Fantasy',
            'rating': 7.5,
            'ticket_price': 350,
            'image': 'https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg',
            'tmdb_id': 346698,
            'overview': 'Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land.',
            'runtime': 114,
            'release_date': '2023-07-19',
            'tmdb_rating': 7.0,
        },
        {
            'name': 'The Dark Knight',
            'tags': 'Movie, Action, Crime, Drama',
            'rating': 9.0,
            'ticket_price': 320,
            'image': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
            'tmdb_id': 155,
            'overview': 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations.',
            'runtime': 152,
            'release_date': '2008-07-16',
            'tmdb_rating': 8.5,
        },
        {
            'name': 'Inception',
            'tags': 'Movie, Action, Sci-Fi, Thriller',
            'rating': 8.8,
            'ticket_price': 320,
            'image': 'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg',
            'tmdb_id': 27205,
            'overview': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'runtime': 148,
            'release_date': '2010-07-15',
            'tmdb_rating': 8.4,
        },
        {
            'name': 'Interstellar',
            'tags': 'Movie, Adventure, Drama, Sci-Fi',
            'rating': 8.7,
            'ticket_price': 350,
            'image': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
            'tmdb_id': 157336,
            'overview': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'runtime': 169,
            'release_date': '2014-11-05',
            'tmdb_rating': 8.4,
        },
    ]
    
    # Concerts
    concerts = [
        {
            'name': 'Arijit Singh Live',
            'tags': 'Concert, Music, Live',
            'rating': 9.5,
            'ticket_price': 2500,
            'image': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
            'overview': 'Experience the magical voice of Arijit Singh live in concert. An unforgettable evening of soulful melodies.',
            'runtime': 180,
        },
        {
            'name': 'Coldplay World Tour',
            'tags': 'Concert, Music, Live, Rock',
            'rating': 9.2,
            'ticket_price': 5000,
            'image': 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=500',
            'overview': 'Coldplay brings their spectacular Music of the Spheres World Tour with stunning visuals and timeless hits.',
            'runtime': 150,
        },
        {
            'name': 'Taylor Swift Eras Tour',
            'tags': 'Concert, Music, Live, Pop',
            'rating': 9.8,
            'ticket_price': 8000,
            'image': 'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=500',
            'overview': 'The Eras Tour is a journey through all of Taylor Swift\'s musical eras, featuring songs from her entire discography.',
            'runtime': 210,
        },
    ]
    
    # Plays
    plays = [
        {
            'name': 'Hamlet',
            'tags': 'Play, Theatre, Drama, Classic',
            'rating': 9.0,
            'ticket_price': 800,
            'image': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=500',
            'overview': 'Shakespeare\'s timeless tragedy of the Prince of Denmark, exploring themes of revenge, mortality, and madness.',
            'runtime': 180,
        },
        {
            'name': 'The Phantom of the Opera',
            'tags': 'Play, Theatre, Musical',
            'rating': 9.3,
            'ticket_price': 1500,
            'image': 'https://images.unsplash.com/photo-1503095396549-807759245b35?w=500',
            'overview': 'Andrew Lloyd Webber\'s legendary musical tells the story of a masked figure who lurks beneath the Paris Opera House.',
            'runtime': 150,
        },
        {
            'name': 'Les Misérables',
            'tags': 'Play, Theatre, Musical, Drama',
            'rating': 9.4,
            'ticket_price': 1200,
            'image': 'https://images.unsplash.com/photo-1516307365426-bea591f05011?w=500',
            'overview': 'The legendary musical about love, sacrifice, and redemption in 19th-century France.',
            'runtime': 170,
        },
    ]
    
    # Events
    events = [
        {
            'name': 'Tech Expo 2025',
            'tags': 'Event, Technology, Exhibition',
            'rating': 8.0,
            'ticket_price': 500,
            'image': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=500',
            'overview': 'Explore the latest innovations in AI, robotics, and emerging technologies at Tech Expo 2025.',
            'runtime': 480,
        },
        {
            'name': 'Comic Con',
            'tags': 'Event, Entertainment, Comics',
            'rating': 8.5,
            'ticket_price': 1000,
            'image': 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=500',
            'overview': 'The ultimate fan experience featuring celebrity panels, exclusive merchandise, and cosplay competitions.',
            'runtime': 600,
        },
        {
            'name': 'Food Festival',
            'tags': 'Event, Food, Festival',
            'rating': 8.2,
            'ticket_price': 300,
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500',
            'overview': 'A culinary celebration featuring cuisines from around the world, cooking demos, and food competitions.',
            'runtime': 360,
        },
    ]

    with flask_app.app_context():
        # Ensure at least one theatre exists
        theatre = Theatre.query.first()
        if not theatre:
            theatre = Theatre(name='Grand Cinema', place='Downtown', capacity=200)
            db.session.add(theatre)
            db.session.commit()
        
        theatre_id = theatre.id
        created = 0
        
        all_shows = classics + modern + concerts + plays + events
        
        for item in all_shows:
            exists = Show.query.filter(Show.name.ilike(item['name'])).first()
            if exists:
                continue

            start = datetime.utcnow() + timedelta(days=created % 14 + 1, hours=created % 6 + 14)
            end = start + timedelta(minutes=item.get('runtime', 120))

            show = Show(
                name=item['name'],
                tags=item['tags'],
                rating=item.get('rating'),
                ticket_price=item['ticket_price'],
                start_time=start,
                end_time=end,
                theatre_id=theatre_id,
                image=item['image'],
                capacity=150,
                tmdb_id=item.get('tmdb_id'),
                overview=item.get('overview'),
                runtime=item.get('runtime'),
                release_date=item.get('release_date'),
                tmdb_rating=item.get('tmdb_rating'),
            )
            db.session.add(show)
            created += 1

        if created:
            db.session.commit()
        print(f"Seed completed. Added {created} shows (movies, concerts, plays, events).")


if __name__ == '__main__':
    ensure_classic_movies()
