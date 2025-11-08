import React from 'react';
import PropTypes from 'prop-types';
import RatingStars from '../Movies/RatingStars';
import { musicService } from '../../services/musicService';
import { FaPlay, FaSpotify } from 'react-icons/fa';

/**
 * Carte affichant les informations d'une piste musicale
 */
const MusicCard = ({ track, onRatingChange, userRating }) => {
    const [isPlaying, setIsPlaying] = React.useState(false);
    const audioRef = React.useRef(null);

    const handleRatingChange = async (newRating) => {
        try {
            if (userRating) {
                await musicService.updateRating(userRating.id, newRating);
            } else {
                await musicService.rateTrack(track.id, newRating);
            }
            if (onRatingChange) {
                onRatingChange(newRating);
            }
        } catch (error) {
            console.error('Error rating track:', error);
        }
    };

    const togglePreview = () => {
        if (!track.preview_url) return;

        if (isPlaying) {
            audioRef.current?.pause();
        } else {
            audioRef.current?.play();
        }
        setIsPlaying(!isPlaying);
    };

    React.useEffect(() => {
        // Créer l'élément audio
        if (track.preview_url) {
            audioRef.current = new Audio(track.preview_url);
            audioRef.current.addEventListener('ended', () => setIsPlaying(false));
        }

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.removeEventListener('ended', () => setIsPlaying(false));
            }
        };
    }, [track.preview_url]);

    return (
        <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white dark:bg-gray-800 hover:shadow-xl transition-shadow duration-300">
            <div className="relative group">
                {track.image_url && (
                    <img
                        className="w-full h-48 object-cover"
                        src={track.image_url}
                        alt={track.title}
                    />
                )}
                {track.preview_url && (
                    <button
                        onClick={togglePreview}
                        className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    >
                        <FaPlay className={`text-white text-4xl ${isPlaying ? 'hidden' : ''}`} />
                        <div className={`w-12 h-12 border-4 border-white rounded-full animate-pulse ${!isPlaying ? 'hidden' : ''}`} />
                    </button>
                )}
            </div>

            <div className="px-6 py-4">
                <div className="font-bold text-xl mb-2 text-gray-800 dark:text-white truncate">
                    {track.title}
                </div>
                <p className="text-gray-600 dark:text-gray-300 text-base mb-2">
                    {track.artist}
                </p>
                {track.album && (
                    <p className="text-gray-500 dark:text-gray-400 text-sm mb-2">
                        Album: {track.album}
                    </p>
                )}
                {track.release_year && (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        {track.release_year}
                    </p>
                )}
            </div>

            <div className="px-6 py-4 flex items-center justify-between">
                <RatingStars
                    rating={userRating ? userRating.rating : 0}
                    onRatingChange={handleRatingChange}
                />
                <a
                    href={`https://open.spotify.com/track/${track.spotify_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-500 hover:text-green-600 transition-colors duration-300"
                >
                    <FaSpotify className="text-2xl" />
                </a>
            </div>
        </div>
    );
};

MusicCard.propTypes = {
    track: PropTypes.shape({
        id: PropTypes.number.isRequired,
        spotify_id: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
        artist: PropTypes.string.isRequired,
        album: PropTypes.string,
        release_year: PropTypes.number,
        preview_url: PropTypes.string,
        image_url: PropTypes.string
    }).isRequired,
    onRatingChange: PropTypes.func,
    userRating: PropTypes.shape({
        id: PropTypes.number.isRequired,
        rating: PropTypes.number.isRequired
    })
};

export default MusicCard;