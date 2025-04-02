import React, { useState, useEffect } from 'react';
import { useOffline } from '../contexts/OfflineContext';

interface SocialActivity {
  id: string;
  type: string;
  timestamp: number;
  user: {
    id: string;
    username: string;
    profile_url: string;
  };
  market_id: string;
  market_ticker: string;
  market_title: string;
  action?: string;
  contracts?: number;
  price?: number;
  comment?: string;
}

interface TrendingMarket {
  series: string;
  activity_count: number;
  trade_count: number;
  comment_count: number;
}

interface SeriesSentiment {
  sentiment: string;
  activity_level: string;
  confidence: string;
  buy_percentage: number;
  sell_percentage: number;
  total_trades: number;
  total_activities: number;
  volume_change: number;
}

interface SocialFeedData {
  status: string;
  timestamp: number;
  activities: SocialActivity[];
  insights: {
    trending_markets: TrendingMarket[];
    series_sentiment: Record<string, SeriesSentiment>;
    overall_sentiment: string;
    activity_level: string;
  };
}

const SocialFeed: React.FC = () => {
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [feedData, setFeedData] = useState<SocialFeedData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'activity' | 'insights'>('activity');

  // Series name mapping for display
  const seriesNameMap: Record<string, string> = {
    'KXNASDAQ100U': 'Nasdaq (Hourly)',
    'KXINXU': 'S&P 500 (Hourly)',
    'KXETHD': 'Ethereum Price (Hourly)',
    'KXETH': 'Ethereum Price Range (Hourly)',
    'KXBTCD': 'Bitcoin Price (Hourly)',
    'KXBTC': 'Bitcoin Price Range (Hourly)'
  };

  // Sentiment color mapping
  const sentimentColorMap: Record<string, string> = {
    'bullish': 'text-green-600',
    'slightly_bullish': 'text-green-400',
    'neutral': 'text-gray-500',
    'slightly_bearish': 'text-red-400',
    'bearish': 'text-red-600'
  };

  // Sentiment display name mapping
  const sentimentNameMap: Record<string, string> = {
    'bullish': 'Bullish',
    'slightly_bullish': 'Slightly Bullish',
    'neutral': 'Neutral',
    'slightly_bearish': 'Slightly Bearish',
    'bearish': 'Bearish'
  };

  // Activity level color mapping
  const activityLevelColorMap: Record<string, string> = {
    'high': 'text-purple-600',
    'medium': 'text-blue-500',
    'low': 'text-gray-500'
  };

  // Fetch social feed data
  useEffect(() => {
    const fetchSocialFeed = async () => {
      if (isOffline) {
        setError('Social feed is not available in offline mode');
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await window.api.fetch('/api/social/feed');
        setFeedData(response);
      } catch (error) {
        console.error('Failed to fetch social feed:', error);
        setError('Failed to fetch social feed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSocialFeed();
    
    // Set up polling for feed updates
    const intervalId = setInterval(() => {
      if (!isOffline) {
        fetchSocialFeed();
      }
    }, 60000); // Update every minute
    
    return () => clearInterval(intervalId);
  }, [isOffline]);

  // Format timestamp
  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Format relative time
  const formatRelativeTime = (timestamp: number): string => {
    const now = Date.now() / 1000;
    const diff = now - timestamp;
    
    if (diff < 60) {
      return 'just now';
    } else if (diff < 3600) {
      const minutes = Math.floor(diff / 60);
      return `${minutes}m ago`;
    } else if (diff < 86400) {
      const hours = Math.floor(diff / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diff / 86400);
      return `${days}d ago`;
    }
  };

  // Render activity item
  const renderActivityItem = (activity: SocialActivity) => {
    return (
      <div key={activity.id} className="border-b border-border p-4 hover:bg-muted/30">
        <div className="flex items-start">
          <div className="flex-shrink-0 mr-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              {activity.user.username.charAt(0).toUpperCase()}
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">
                {activity.user.username}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatRelativeTime(activity.timestamp)}
              </p>
            </div>
            
            <p className="text-sm text-muted-foreground mb-1">
              {activity.market_title}
            </p>
            
            {activity.type === 'trade' && (
              <div className="flex items-center mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  activity.action === 'YES' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {activity.action}
                </span>
                <span className="ml-2 text-sm">
                  {activity.contracts} contract{activity.contracts !== 1 ? 's' : ''} @ {activity.price}¢
                </span>
              </div>
            )}
            
            {activity.type === 'comment' && (
              <p className="text-sm mt-1 p-2 bg-muted rounded-md">
                {activity.comment}
              </p>
            )}
            
            {activity.type === 'like' && (
              <p className="text-sm mt-1 text-muted-foreground">
                Liked this market
              </p>
            )}
            
            {activity.type === 'follow' && (
              <p className="text-sm mt-1 text-muted-foreground">
                Started following this market
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Render trending markets
  const renderTrendingMarkets = () => {
    if (!feedData || !feedData.insights.trending_markets.length) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          No trending markets found
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {feedData.insights.trending_markets.map((market) => {
          const sentiment = feedData.insights.series_sentiment[market.series] || {
            sentiment: 'neutral',
            activity_level: 'low',
            confidence: 'low',
            buy_percentage: 50,
            sell_percentage: 50
          };
          
          return (
            <div key={market.series} className="bg-card rounded-lg shadow-sm p-4">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-medium">
                  {seriesNameMap[market.series] || market.series}
                </h3>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  sentimentColorMap[sentiment.sentiment] || 'text-gray-500'
                }`}>
                  {sentimentNameMap[sentiment.sentiment] || 'Neutral'}
                </div>
              </div>
              
              <div className="mt-2 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Activity Level</p>
                  <p className={`text-sm font-medium ${
                    activityLevelColorMap[sentiment.activity_level] || 'text-gray-500'
                  }`}>
                    {sentiment.activity_level.charAt(0).toUpperCase() + sentiment.activity_level.slice(1)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Confidence</p>
                  <p className="text-sm font-medium">
                    {sentiment.confidence.charAt(0).toUpperCase() + sentiment.confidence.slice(1)}
                  </p>
                </div>
              </div>
              
              <div className="mt-4">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>Buy Sentiment</span>
                  <span>Sell Sentiment</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2.5 flex">
                  <div 
                    className="bg-green-500 h-2.5 rounded-l-full" 
                    style={{ width: `${sentiment.buy_percentage}%` }}
                  ></div>
                  <div 
                    className="bg-red-500 h-2.5 rounded-r-full" 
                    style={{ width: `${sentiment.sell_percentage}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs mt-1">
                  <span>{sentiment.buy_percentage.toFixed(1)}%</span>
                  <span>{sentiment.sell_percentage.toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="mt-4 flex justify-between text-sm">
                <div>
                  <span className="text-muted-foreground">Total Activities:</span> {market.activity_count}
                </div>
                <div>
                  <span className="text-muted-foreground">Trades:</span> {market.trade_count}
                </div>
                <div>
                  <span className="text-muted-foreground">Comments:</span> {market.comment_count}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Render overall sentiment
  const renderOverallSentiment = () => {
    if (!feedData) return null;
    
    const { overall_sentiment, activity_level } = feedData.insights;
    
    return (
      <div className="bg-card rounded-lg shadow-sm p-4 mb-6">
        <h3 className="text-lg font-medium mb-2">Overall Market Sentiment</h3>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-muted-foreground">Sentiment</p>
            <p className={`text-lg font-medium ${
              sentimentColorMap[overall_sentiment] || 'text-gray-500'
            }`}>
              {sentimentNameMap[overall_sentiment] || 'Neutral'}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Activity Level</p>
            <p className={`text-lg font-medium ${
              activityLevelColorMap[activity_level] || 'text-gray-500'
            }`}>
              {activity_level.charAt(0).toUpperCase() + activity_level.slice(1)}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Last Updated</p>
            <p className="text-lg font-medium">
              {feedData.timestamp ? formatTimestamp(feedData.timestamp) : 'Unknown'}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Kalshi Social Feed</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('activity')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              activeTab === 'activity' 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Activity Feed
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              activeTab === 'insights' 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Market Insights
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && !feedData && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary border-r-transparent"></div>
          <p className="mt-2 text-muted-foreground">Loading social feed data...</p>
        </div>
      )}

      {/* Content */}
      {!isLoading && !error && feedData && (
        <>
          {activeTab === 'activity' && (
            <div>
              <div className="bg-card rounded-lg shadow-md overflow-hidden">
                <div className="p-4 bg-muted/50 border-b border-border">
                  <h2 className="text-lg font-medium">Recent Activity</h2>
                </div>
                <div className="divide-y divide-border">
                  {feedData.activities.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      No recent activity found
                    </div>
                  ) : (
                    feedData.activities.map(renderActivityItem)
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'insights' && (
            <div>
              {renderOverallSentiment()}
              
              <h2 className="text-xl font-semibold mb-4">Trending Markets</h2>
              {renderTrendingMarkets()}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SocialFeed;
