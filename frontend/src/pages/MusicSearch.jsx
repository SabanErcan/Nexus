import React from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../components/Common/SearchBar';
import MusicGrid from '../components/Music/MusicGrid';
import { musicService } from '../services/musicService';

/**
 * Page de recherche musicale
 */
const MusicSearch = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [tracks, setTracks] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [userRatings, setUserRatings] = React.useState([]);
    const [total, setTotal] = React.useState(0);
    const [page, setPage] = React.useState(1);

    const query = searchParams.get('q') || '';
    const limit = 20;

    React.useEffect(() => {
        const loadUserRatings = async () => {
            try {
                const ratings = await musicService.getUserRatings();
                setUserRatings(ratings);
            } catch (error) {
                console.error('Error loading user ratings:', error);
            }
        };

        loadUserRatings();
    }, []);

    React.useEffect(() => {
        const searchTracks = async () => {
            if (!query) {
                setTracks([]);
                setTotal(0);
                return;
            }

            setLoading(true);
            try {
                const offset = (page - 1) * limit;
                const results = await musicService.searchTracks(query, limit, offset);
                setTracks(results.items);
                setTotal(results.total);
            } catch (error) {
                console.error('Error searching tracks:', error);
            } finally {
                setLoading(false);
            }
        };

        searchTracks();
    }, [query, page]);

    const handleSearch = (searchQuery) => {
        setPage(1);
        setSearchParams(searchQuery ? { q: searchQuery } : {});
    };

    const handleRatingChange = async (trackId, rating) => {
        try {
            const existingRating = userRatings.find((r) => r.track_id === trackId);
            
            if (existingRating) {
                const updatedRating = await musicService.updateRating(existingRating.id, rating);
                setUserRatings(userRatings.map((r) => 
                    r.id === updatedRating.id ? updatedRating : r
                ));
            } else {
                const newRating = await musicService.rateTrack(trackId, rating);
                setUserRatings([...userRatings, newRating]);
            }
        } catch (error) {
            console.error('Error updating rating:', error);
        }
    };

    const totalPages = Math.ceil(total / limit);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-8">
                Recherche musicale
            </h1>

            <SearchBar
                initialValue={query}
                onSearch={handleSearch}
                placeholder="Rechercher des artistes, titres ou albums..."
            />

            <MusicGrid
                tracks={tracks}
                loading={loading}
                onRatingChange={handleRatingChange}
                userRatings={userRatings}
            />

            {totalPages > 1 && (
                <div className="flex justify-center mt-8 gap-2">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
                    >
                        Précédent
                    </button>
                    <span className="px-4 py-2">
                        Page {page} sur {totalPages}
                    </span>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
                    >
                        Suivant
                    </button>
                </div>
            )}
        </div>
    );
};

export default MusicSearch;