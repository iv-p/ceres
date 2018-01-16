CREATE TABLE minute (timestamp integer, open real, high real, low real, clos real, volume real, asset_volume real, trades integer, buy_base_volume real, buy_quote_volume real, PRIMARY KEY (timestamp))
CREATE TABLE hour (timestamp integer, open real, high real, low real, clos real, volume real, asset_volume real, trades integer, buy_base_volume real, buy_quote_volume real, PRIMARY KEY (timestamp))
CREATE TABLE day (timestamp integer, open real, high real, low real, clos real, volume real, asset_volume real, trades integer, buy_base_volume real, buy_quote_volume real, PRIMARY KEY (timestamp))

CREATE TABLE event (timestamp integer, polarity real, subjectivity real, PRIMARY KEY (timestamp))