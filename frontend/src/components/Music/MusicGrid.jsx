import React from 'react';
import PropTypes from 'prop-types';
import MusicCard from './MusicCard';
import Loading from '../Common/Loading';

/**
 * Grille de cartes musicales
 */
const MusicGrid = ({ tracks, loading, onRatingChange, userRatings }) => {
    if (loading) {
        return <Loading />;
    }

    if (!tracks || tracks.length === 0) {
        return (
            <div className="text-center text-gray-600 dark:text-gray-300 mt-8">
                Aucune piste trouvée
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6">
            {tracks.map((track) => (
                <MusicCard
                    key={track.id}
                    track={track}
                    onRatingChange={(rating) => onRatingChange(track.id, rating)}
                    userRating={userRatings?.find((r) => r.track_id === track.id)}
                />
            ))}
        </div>
    );
};

MusicGrid.propTypes = {
    tracks: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            spotify_id: PropTypes.string.isRequired,
            title: PropTypes.string.isRequired,
            artist: PropTypes.string.isRequired,
            album: PropTypes.string,
            release_year: PropTypes.number,
            preview_url: PropTypes.string,
            image_url: PropTypes.string
        })
    ),
    loading: PropTypes.bool,
    onRatingChange: PropTypes.func.isRequired,
    userRatings: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            track_id: PropTypes.number.isRequired,
            rating: PropTypes.number.isRequired
        })
    )
};

MusicGrid.defaultProps = {
    loading: false,
    tracks: [],
    userRatings: []
};

export default MusicGrid;