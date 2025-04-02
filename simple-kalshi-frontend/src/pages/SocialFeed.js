import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useOffline } from '../contexts/OfflineContext';

const SocialFeed = () => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline, cachedData, cacheData } = useOffline();
  
  const [activeTab, setActiveTab] = useState('activity');
  const [activityFeed, setActivityFeed] = useState([]);
  const [marketInsights, setMarketInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch social feed data
  useEffect(() => {
    const fetchSocialFeed = async () => {
      if (isOffline) {
        if (cachedData.socialFeed) {
          setActivityFeed(cachedData.socialFeed.activity || []);
          setMarketInsights(cachedData.socialFeed.insights || []);
        }
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const [activityData, insightsData] = await Promise.all([
          apiRequest('get', '/api/social/activity'),
          apiRequest('get', '/api/social/insights')
        ]);
        
        setActivityFeed(activityData);
        setMarketInsights(insightsData);
        
        // Cache the data
        cacheData('socialFeed', {
          activity: activityData,
          insights: insightsData,
          lastUpdated: new Date().toISOString()
        });
      } catch (error) {
        setError('Failed to fetch social feed data');
        
        // Use cached data if available
        if (cachedData.socialFeed) {
          setActivityFeed(cachedData.socialFeed.activity || []);
          setMarketInsights(cachedData.socialFeed.insights || []);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchSocialFeed();
  }, [isConnected, isOffline]);

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  // Get sentiment color
  const getSentimentColor = (sentiment) => {
    if (sentiment === 'bullish') return 'text-green-600';
    if (sentiment === 'bearish') return 'text-red-600';
    return 'text-gray-600';
  };

  // Get activity icon
  const getActivityIcon = (type) => {
    switch (type) {
      case 'trade':
        return (
          <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        ) ;
      case 'comment':
        return (
          <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        ) ;
      case 'like':
        return (
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        ) ;
      default:
        return (
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        ) ;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Social Feed</h1>
        {isOffline && (
          <span className="px-2 py-1 text-xs font-medium rounded-md bg-yellow-100 text-yellow-800">
            Offline Mode - Showing Cached Data
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('activity')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'activity'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Activity Feed
            </button>
            <button
              onClick={() => setActiveTab('insights')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'insights'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Market Insights
            </button>
          </nav>
        </div>

        <div className="mt-4">
          {isLoading ? (
            <p>Loading social feed data...</p>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <>
              {/* Activity Feed Tab */}
              {activeTab === 'activity' && (
                <div className="space-y-4">
                  {activityFeed.length === 0 ? (
                    <p className="text-gray-500 dark:text-gray-400">No activity to display.</p>
                  ) : (
                    activityFeed.map((activity) => (
                      <div key={activity.id} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0">
                        <div className="flex items-start">
                          <div className="flex-shrink-0 mr-3">
                            {getActivityIcon(activity.type)}
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between">
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {activity.user}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {formatTime(activity.timestamp)}
                              </p>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                              {activity.type === 'trade' && (
                                <>
                                  <span className={activity.action === 'buy' ? 'text-green-600' : 'text-red-600'}>
                                    {activity.action === 'buy' ? 'Bought' : 'Sold'}
                                  </span>
                                  {' '}
                                  <span className="font-medium">{activity.outcome}</span>
                                  {' in '}
                                  <span className="font-medium">{activity.market}</span>
                                  {' at '}
                                  <span className="font-medium">${activity.price.toFixed(2)}</span>
                                </>
                              )}
                              {activity.type === 'comment' && (
                                <>
                                  <span>Commented on </span>
                                  <span className="font-medium">{activity.market}</span>
                                  <p className="mt-1 p-2 bg-gray-50 dark:bg-gray-800 rounded-md">
                                    "{activity.content}"
                                  </p>
                                </>
                              )}
                              {activity.type === 'like' && (
                                <>
                                  <span>Liked </span>
                                  <span className="font-medium">{activity.market}</span>
                                </>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Market Insights Tab */}
              {activeTab === 'insights' && (
                <div className="space-y-6">
                  {marketInsights.length === 0 ? (
                    <p className="text-gray-500 dark:text-gray-400">No market insights to display.</p>
                  ) : (
                    marketInsights.map((insight) => (
                      <div key={insight.id} className="card border border-gray-200 dark:border-gray-700">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium text-gray-900 dark:text-white">{insight.market}</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{insight.series}</p>
                          </div>
                          <div className="flex items-center">
                            <span className={`text-sm font-medium ${getSentimentColor(insight.sentiment)}`}>
                              {insight.sentiment.charAt(0).toUpperCase() + insight.sentiment.slice(1)}
                            </span>
                            <span className="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                              {insight.activity_level} Activity
                            </span>
                          </div>
                        </div>
                        
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sentiment Analysis</h4>
                            <div className="flex items-center">
                              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div 
                                  className="bg-blue-600 h-2.5 rounded-full" 
                                  style={{ width: `${insight.buy_sentiment}%` }}
                                ></div>
                              </div>
                              <div className="ml-2 text-xs font-medium">
                                <span className="text-green-600">{insight.buy_sentiment}%</span>
                                {' / '}
                                <span className="text-red-600">{insight.sell_sentiment}%</span>
                              </div>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              Buy vs Sell Sentiment
                            </p>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Key Metrics</h4>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Volume</p>
                                <p className="text-sm font-medium">${insight.volume.toFixed(2)}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Trades</p>
                                <p className="text-sm font-medium">{insight.trade_count}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Comments</p>
                                <p className="text-sm font-medium">{insight.comment_count}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Confidence</p>
                                <p className="text-sm font-medium">{insight.confidence}%</p>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {insight.trending_comments && insight.trending_comments.length > 0 && (
                          <div className="mt-4">
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Trending Comments</h4>
                            <div className="space-y-2">
                              {insight.trending_comments.map((comment, index) => (
                                <div key={index} className="p-2 bg-gray-50 dark:bg-gray-800 rounded-md">
                                  <p className="text-sm text-gray-600 dark:text-gray-300">"{comment.content}"</p>
                                  <div className="flex justify-between mt-1">
                                    <p className="text-xs text-gray-500 dark:text-gray-400">{comment.user}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">{formatTime(comment.timestamp)}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialFeed; 