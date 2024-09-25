from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
from .models import Rating
import pandas as pd

def get_recommendations_for_user(user_id, num_recommendations=5):
    # Fetch all ratings
    ratings = Rating.objects.all().values('student', 'course', 'rating')

    # Convert to DataFrame
    df = pd.DataFrame(list(ratings))

    if df.empty:
        return []  # Return an empty list if there are no ratings

    # Define the Reader and load the data
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['student', 'course', 'rating']], reader)

    # Split data into training and test sets
    trainset, testset = train_test_split(data, test_size=0.25)

    # Build and train the SVD model
    model = SVD()
    model.fit(trainset)

    # Predict ratings for the testset
    predictions = model.test(testset)

    # Create a DataFrame of predictions
    predictions_df = pd.DataFrame(predictions, columns=['uid', 'iid', 'true_r', 'est', 'details'])

    # Get recommendations for the specified user
    user_predictions = predictions_df[predictions_df['uid'] == user_id]

    if user_predictions.empty:
        return []  # Return an empty list if no predictions are available

    # Sort by estimated rating
    user_recommendations = user_predictions.sort_values(by='est', ascending=False)

    # Get the top recommendations
    top_recommendations = user_recommendations.head(num_recommendations)

    # Return the recommended course IDs
    recommended_course_ids = top_recommendations['iid'].tolist()

    return recommended_course_ids
