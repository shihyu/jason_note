use std::{
    fs::read_dir,
    iter::{empty, once},
    path::{Path, PathBuf},
};

use options::SubCommand;
use v8chart::{load_from_json, write_to_csv, DataSet};

mod http;
mod options;
mod v8chart;
#[macro_use]
extern crate log;

/// recursively walk a directory
fn walk_dir<P: AsRef<Path>>(dir: P, recursive: bool) -> Box<dyn Iterator<Item = PathBuf>> {
    match read_dir(dir) {
        Ok(result) => Box::new(
            result
                .map(|res| res.map(|e| e.path()))
                .filter_map(|res| res.ok())
                .flat_map(move |path| {
                    if recursive && path.is_dir() {
                        walk_dir(path, recursive)
                    } else {
                        Box::new(once(path))
                    }
                }),
        ),
        _ => Box::new(empty()),
    }
}

/// convert a json at a path to CSVs in the same path
fn convert(path: PathBuf) {
    match load_from_json(path.as_path().to_str().unwrap()) {
        Ok(chart_wrapper) => {
            let ds_vec: Vec<DataSet> = chart_wrapper.chart.into();

            let outputs = if ds_vec.len() == 1 {
                vec![path.with_extension("csv")]
            } else {
                let stem = path
                    .file_stem()
                    .map_or("unknown_stem", |s| s.to_str().unwrap())
                    .to_string();
                (0..ds_vec.len())
                    .map(|i| path.with_file_name(format!("{:?}_{}.csv", stem, i)))
                    .collect()
            };

            ds_vec.iter().zip(outputs.iter()).for_each(|(ds, path)| {
                if let Err(err) = write_to_csv(ds, path) {
                    error!("failed to write to csv {:?} with {:?}", path, err);
                } else {
                    info!("successfully converted to {:?}", path);
                }
            });
        }
        Err(err) => error!("failed to load json from {:?} with {:?}", path, err),
    }
}

/// wrapper over [`convert`] and [`walk_dir`]
fn convert_to_csv(json_dir: &str, recursive: bool) -> std::io::Result<()> {
    walk_dir(json_dir, recursive)
        .filter(|path| path.extension().map_or(false, |ext| ext == "json"))
        .for_each(convert);
    Ok(())
}

#[tokio::main]
async fn main() {
    env_logger::init();
    let opts = options::parse();
    match opts.subcmd {
        SubCommand::Download(opts) => {
            if let Some(start) = opts.start {
                if let Some(end) = opts.end {
                    if start >= end {
                        panic!("start date is greater or equal to end date")
                    }
                }
            }
            let results = http::download(&opts).await;
            if opts.convert {
                results.into_iter().for_each(|(p, res)| {
                    if res.is_ok() {
                        convert(p);
                    }
                });
            }
        }
        SubCommand::Convert(opts) => {
            if let Err(err) = convert_to_csv(&opts.input_dir, opts.recursive) {
                error!("failed to walk dir {} with {:?}", opts.input_dir, err);
            }
        }
    };
}
