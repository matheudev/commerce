# Commerce

Commerce is an auction web application where users can create new listings, bid, comment on listings, and more.

## Features

- **Models:** The application has three models in addition to the User model: one for auction listings, one for bids, and one for comments made on auction listings. Users can have additional models if needed.
- **Create Listing:** Users can create a new listing by specifying a title, description, starting bid, and optionally, a URL for an image and a category.
- **Active Listings Page:** Users can view all active auction listings, which displays the title, description, current price, and photo (if one exists for the listing).
- **Listing Page:** Users can view all details about the listing, including the current price for the listing. If the user is signed in, they can add the item to their watchlist or bid on the item. The user can also close the auction if they are the one who created the listing. If the user has won the auction, the page will indicate so.
- **Watchlist:** Users can view all listings they have added to their watchlist, and clicking on any of those listings will take the user to that listing's page.
- **Categories:** Users can view all listing categories, and clicking on any of those categories will display all active listings in that category.
- **Django Admin Interface:** Site administrators can view, add, edit, and delete any listings, comments, and bids made on the site.

## Credits

This project was completed as part of the CS50W course offered by Harvard University.
