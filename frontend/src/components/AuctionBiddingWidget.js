import React, { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import io from "socket.io-client";
import {
  Gavel, TrendingUp, Clock, Users, DollarSign, Zap,
  Loader2, CheckCircle, AlertCircle
} from "lucide-react";
import { useAuth, API, BACKEND_URL } from "../App";

export const AuctionBiddingWidget = ({ product }) => {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [bidAmount, setBidAmount] = useState("");
  const [socket, setSocket] = useState(null);
  const [realtimeBids, setRealtimeBids] = useState([]);

  // Get product bids
  const { data: bidsData } = useQuery({
    queryKey: ["product-bids", product.id],
    queryFn: () => axios.get(`${API}/products/${product.id}/bids`).then(r => r.data),
    refetchInterval: 5000 // Fallback polling every 5s
  });

  const bids = realtimeBids.length > 0 ? realtimeBids : (bidsData?.bids || []);
  const highestBid = bids[0];
  const minBid = highestBid ? highestBid.amount + 1 : (product.starting_price || product.price || 0);

  // Socket.IO connection for real-time updates
  useEffect(() => {
    const newSocket = io(BACKEND_URL, {
      path: '/api/socket.io',
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('✅ Socket.IO connected');
      // Join this product's auction room
      newSocket.emit('join_auction', { product_id: product.id });
    });

    newSocket.on(`new_bid:${product.id}`, (data) => {
      console.log('🔔 New bid received:', data);
      // Update bids in real-time
      setRealtimeBids(prev => [data.bid, ...prev.filter(b => b.id !== data.bid.id)]);
      
      if (data.bid.user_id !== user?.id) {
        toast.info(`New bid: $${data.bid.amount} by ${data.bid.username}`);
      }
    });

    newSocket.on('joined_auction', (data) => {
      console.log('Joined auction room:', data.product_id);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.emit('leave_auction', { product_id: product.id });
        newSocket.disconnect();
      }
    };
  }, [product.id, user?.id, BACKEND_URL]);

  // Place bid mutation
  const placeBid = useMutation({
    mutationFn: (amount) => axios.post(
      `${API}/products/${product.id}/bid`,
      { amount: parseFloat(amount) },
      { headers: { Authorization: `Bearer ${token}` }}
    ).then(r => r.data),
    onSuccess: (data) => {
      toast.success("Bid placed successfully! 🎉");
      setBidAmount("");
      queryClient.invalidateQueries(["product-bids", product.id]);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || "Failed to place bid";
      toast.error(message);
    }
  });

  const handlePlaceBid = () => {
    const amount = parseFloat(bidAmount);
    
    if (!user) {
      toast.error("Please login to place a bid");
      return;
    }

    if (isNaN(amount) || amount < minBid) {
      toast.error(`Minimum bid is $${minBid}`);
      return;
    }

    placeBid.mutate(amount);
  };

  if (!product.is_auction) {
    return null;
  }

  const isUserHighestBidder = highestBid && user && highestBid.user_id === user.id;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
          <Gavel className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-rajdhani text-xl font-bold">Live Auction</h3>
          <div className="flex items-center gap-2 text-sm text-white/60">
            <Zap className="w-3 h-3 text-green-400" />
            <span>Real-time bidding active</span>
          </div>
        </div>
      </div>

      {/* Current Bid Info */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-lg bg-white/5">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-cyan-400" />
            <span className="text-sm text-white/60">Current Bid</span>
          </div>
          <p className="text-2xl font-bold text-cyan-400">
            ${highestBid ? highestBid.amount : product.starting_price || 0}
          </p>
          {highestBid && (
            <p className="text-xs text-white/40 mt-1">by @{highestBid.username}</p>
          )}
        </div>

        <div className="p-4 rounded-lg bg-white/5">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-white/60">Total Bids</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">{bids.length}</p>
        </div>
      </div>

      {/* Bid Status Alert */}
      {isUserHighestBidder && (
        <div className="mb-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <p className="text-sm text-green-100">
            <strong>You're winning!</strong> You have the highest bid.
          </p>
        </div>
      )}

      {/* Place Bid */}
      {user ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Your Bid Amount</label>
            <div className="flex gap-3">
              <div className="relative flex-1">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                  type="number"
                  value={bidAmount}
                  onChange={(e) => setBidAmount(e.target.value)}
                  placeholder={`Min: $${minBid}`}
                  min={minBid}
                  step="1"
                  className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/10 border border-white/20 focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <button
                onClick={handlePlaceBid}
                disabled={placeBid.isPending || !bidAmount}
                className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2 whitespace-nowrap"
              >
                {placeBid.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Gavel className="w-4 h-4" />
                )}
                Place Bid
              </button>
            </div>
            <p className="text-xs text-white/40 mt-2">
              Minimum bid: ${minBid} • Increment: $1
            </p>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-400" />
          <p className="text-sm text-yellow-100">
            Please <a href="/login" className="underline font-semibold">login</a> to place a bid
          </p>
        </div>
      )}

      {/* Recent Bids */}
      {bids.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            Recent Bids
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            <AnimatePresence>
              {bids.slice(0, 10).map((bid, idx) => (
                <motion.div
                  key={bid.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    idx === 0 
                      ? 'bg-cyan-500/20 border border-cyan-500/30' 
                      : 'bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {idx === 0 && <Gavel className="w-4 h-4 text-cyan-400" />}
                    <div>
                      <p className="font-medium text-sm">
                        @{bid.username}
                        {bid.user_id === user?.id && (
                          <span className="ml-2 text-xs text-cyan-400">(You)</span>
                        )}
                      </p>
                      <p className="text-xs text-white/40">
                        {new Date(bid.placed_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <span className={`font-bold ${idx === 0 ? 'text-cyan-400' : 'text-white/80'}`}>
                    ${bid.amount}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Auction Info */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-white/60">
            <Clock className="w-4 h-4" />
            <span>Auction ends: 24h</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-green-400 text-xs">Live</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
